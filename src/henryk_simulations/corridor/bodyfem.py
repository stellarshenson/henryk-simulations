"""FEM body-impact sound - the deforming torso pushes air, the air is the sound.

Notebook 03's model. The body never radiates as a source in its own right;
it is a moving boundary. The impact deforms the torso, the torso's surface
moves, and the only thing that reaches the microphone is the air that
surface pushes.

A real 3D body-skin mesh (BodyParts3D, decimated) is loaded and the upper
torso - the part that struck the wall - is isolated. That torso is
voxelised into a tetrahedral solid; scikit-fem assembles its 3D linear-
elastic stiffness and mass; an eigensolve gives the soft-tissue
deformation modes. The thorax is treated as compressible - it is an
air-filled bag (the lungs), so the impact squash genuinely changes its
volume and the chest wall works as a bellows. The contact pulse drives
that squash; the net volume velocity of the deforming surface (the air it
pushes) radiates to the microphone as a compact monopole.

Because the modes sit in the tens-of-hertz band and soft tissue is heavily
damped, the pushed air carries a low thump - not the tonal ring of a hard,
resonant object.

The body surface is uneven, and that roughness enters twice. It textures
the contact force the modes are driven by, graining the thump. And the air
trapped in the closing wall-body gap is squeezed out through the irregular
gap as the body lands - a brief broadband burst, far higher in pitch than
the thump. The microphone hears the two summed.

The pipeline: ``load_body_mesh`` -> ``isolate_upper_torso`` ->
``voxelise_torso`` -> ``assemble_fem`` -> ``solve_modes`` -> the textured
contact pulse drives ``impact_response`` -> ``radiate_modes`` for the thump
and ``air_escape`` for the squeezed-air burst -> their sum at the
microphone. ``solve_body_fem`` runs the whole chain.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import meshio
import numpy as np
from scipy.signal import butter, lsim, sosfiltfilt
from scipy.sparse.linalg import eigsh
from scipy.spatial import ConvexHull, Delaunay
from skfem import Basis, BilinearForm, ElementTetP1, ElementVector, MeshTet
from skfem.helpers import dot
from skfem.models.elasticity import lame_parameters, linear_elasticity

from henryk_simulations.config import PROJ_ROOT

P_REF = 20e-6  # Pa, reference sound pressure

# the six tetrahedra of a voxel cube, sharing the 0-7 space diagonal
_TET6 = ((0, 7, 1, 3), (0, 7, 3, 2), (0, 7, 2, 6), (0, 7, 6, 4), (0, 7, 4, 5), (0, 7, 5, 1))
_CORNERS = ((0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0),
            (0, 0, 1), (1, 0, 1), (0, 1, 1), (1, 1, 1))


@dataclass(frozen=True)
class BodyFEMConfig:
    """Configuration for the FEM body-impact sound model."""

    # body mesh and upper-torso isolation
    mesh_path: str = "data/external/body_mesh/body-skin.obj"
    torso_z_lo_frac: float = 0.62  # fraction of body height, lower cut
    torso_z_hi_frac: float = 0.84  # fraction of body height, upper cut
    torso_x_halfwidth: float = 0.20  # m, half-width kept about the body axis (trims the arms)
    # impact - the body delivered to the door by notebook 01's envelope
    m_eff: float = 30.0  # kg, effective upper-torso impacting mass (for the contact force)
    v_close: float = 2.74  # m/s, closing velocity (notebook 01 no-coast)
    restitution: float = 0.25  # rebound coefficient off the rigid door
    contact_time: float = 0.030  # s, contact duration
    # finite-element model
    voxel_size: float = 0.022  # m, FEM voxel edge
    youngs_modulus: float = 5.0e5  # Pa, soft-tissue elastic modulus
    poisson: float = 0.35  # effective - the air-filled thorax (lungs) compresses
    density: float = 1000.0  # kg/m^3
    modal_damping: float = 0.20  # heavily damped soft tissue - the modes do not ring long
    n_modes: int = 12  # elastic deformation modes retained
    # acoustics
    air_rho: float = 1.2  # kg/m^3
    air_c: float = 343.0  # m/s
    mic_distance: float = 1.0  # m, microphone distance
    sample_rate: int = 44100  # Hz
    t_max: float = 0.30  # s, output window
    # air escape - the air squeezed out of the closing wall-body gap
    contact_patch_area: float = 0.035  # m^2, back contact patch area
    gap_squeeze_start: float = 0.006  # m, gap where the trapped air film starts to matter
    gap_seal: float = 0.0015  # m, residual gap left by the uneven body surface
    escape_band_lo: float = 300.0  # Hz, lower edge of the escape-noise band
    escape_band_hi: float = 6000.0  # Hz, upper edge of the escape-noise band
    escape_seed: int = 0  # rng seed for the squeezed-air texture noise
    # surface texture - the uneven body surface graining the contact
    surface_roughness: float = 0.25  # uneven-surface modulation depth of the contact force
    roughness_seed: int = 1  # rng seed for the surface-roughness noise


@dataclass(frozen=True)
class TorsoMesh:
    """The isolated upper-torso surface mesh and its derived measures."""

    points: np.ndarray  # (V, 3) m
    triangles: np.ndarray  # (F, 3) int
    area: float  # m^2, convex-hull surface area
    volume: float  # m^3, convex-hull volume
    centroid: np.ndarray  # (3,) m


@dataclass(frozen=True)
class TorsoFEM:
    """The voxelised torso solid and its solved deformation modes."""

    nodes: np.ndarray  # (N, 3) m
    tets: np.ndarray  # (T, 4) int
    frequencies: np.ndarray  # (n_modes,) Hz - elastic mode frequencies
    shapes: np.ndarray  # (n_modes, N, 3) nodal displacement mode shapes
    volume_velocity: np.ndarray  # (n_modes,) m^3 - air pushed per unit modal amplitude


@dataclass(frozen=True)
class BodyFEMResult:
    """Solved FEM body-impact sound at the microphone."""

    config: BodyFEMConfig
    torso: TorsoMesh
    fem: TorsoFEM
    t: np.ndarray  # s
    modal_amplitude: np.ndarray  # (n_modes, n_t) modal displacement q_i(t)
    surface_deflection: float  # m, peak surface displacement
    pressure_thump: np.ndarray  # Pa, the FEM body thump (low frequency)
    pressure_escape: np.ndarray  # Pa, the squeezed-air burst (high frequency, textured)
    pressure: np.ndarray  # Pa, total sound at the microphone
    peak_spl: float  # dB SPL of the total


def load_body_mesh(cfg: BodyFEMConfig | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Load the decimated 3D body-skin surface mesh (points in metres)."""
    if cfg is None:
        cfg = BodyFEMConfig()
    path = Path(cfg.mesh_path)
    if not path.is_absolute():
        path = PROJ_ROOT / path
    mesh = meshio.read(path)
    points = np.asarray(mesh.points, dtype=float)
    triangles = np.asarray(mesh.cells_dict["triangle"], dtype=np.int64)
    return points, triangles


def isolate_upper_torso(
    points: np.ndarray, triangles: np.ndarray, cfg: BodyFEMConfig | None = None
) -> TorsoMesh:
    """Isolate the upper torso from the body mesh.

    Keeps the band of the body between ``torso_z_lo_frac`` and
    ``torso_z_hi_frac`` of its height, and trims the arms by keeping only
    vertices within ``torso_x_halfwidth`` of the body axis. The upper
    torso is the part that struck the wall.
    """
    if cfg is None:
        cfg = BodyFEMConfig()
    z = points[:, 2]
    z_lo, z_hi = z.min(), z.max()
    height = z_hi - z_lo
    band_lo = z_lo + cfg.torso_z_lo_frac * height
    band_hi = z_lo + cfg.torso_z_hi_frac * height
    x_axis = np.median(points[:, 0])

    keep = (
        (z >= band_lo) & (z <= band_hi) & (np.abs(points[:, 0] - x_axis) <= cfg.torso_x_halfwidth)
    )
    face_keep = np.all(keep[triangles], axis=1)
    tris = triangles[face_keep]
    used = np.unique(tris)
    remap = -np.ones(len(points), dtype=np.int64)
    remap[used] = np.arange(len(used))
    torso_points = points[used]
    torso_tris = remap[tris]

    # the upper torso is convex-barrel-like; the convex hull gives a robust
    # volume and surface area, free of the scan's surface-detail crinkle
    hull = ConvexHull(torso_points)
    return TorsoMesh(
        points=torso_points,
        triangles=torso_tris,
        area=float(hull.area),
        volume=float(hull.volume),
        centroid=torso_points.mean(axis=0),
    )


def deceleration_pulse(cfg: BodyFEMConfig) -> tuple[np.ndarray, np.ndarray]:
    """The body's deceleration over the impact - a smooth sine-squared
    pulse. The impulse integrates to the velocity change v_close*(1+e),
    so the body is brought to rest and rebounds."""
    n = int(cfg.t_max * cfg.sample_rate)
    t = np.arange(n) / cfg.sample_rate
    delta_v = cfg.v_close * (1.0 + cfg.restitution)
    a_peak = 2.0 * delta_v / cfg.contact_time  # integral of sin^2 over the pulse = tau/2
    accel = np.zeros_like(t)
    inside = t < cfg.contact_time
    accel[inside] = a_peak * np.sin(np.pi * t[inside] / cfg.contact_time) ** 2
    return t, accel


def peak_spl(pressure: np.ndarray) -> float:
    """Peak sound pressure level, dB re 20 uPa."""
    peak = float(np.abs(pressure).max())
    return 20.0 * np.log10(peak / P_REF) if peak > 0 else 0.0


def _a_weighting(freq: np.ndarray) -> np.ndarray:
    """A-weighting gain (linear) at each frequency - IEC 61672."""
    f2 = freq.astype(float) ** 2
    ra = (12194.0**2 * f2**2) / (
        (f2 + 20.6**2)
        * np.sqrt((f2 + 107.7**2) * (f2 + 737.9**2))
        * (f2 + 12194.0**2)
    )
    return ra * 10.0 ** (2.0 / 20.0)  # +2 dB normalisation at 1 kHz


def sound_levels(pressure: np.ndarray, sample_rate: int) -> dict[str, float]:
    """Peak, RMS and A-weighted SPL of a pressure signal, dB re 20 uPa.

    The peak and RMS levels are flat (Z-weighted). The A-weighted level
    applies the IEC 61672 curve, which heavily attenuates the low
    frequencies a body thump lives in - so a dBA meter reads it far below
    the flat peak.
    """
    peak = float(np.abs(pressure).max())
    rms = float(np.sqrt(np.mean(pressure**2)))
    spec = np.fft.rfft(pressure)
    freq = np.fft.rfftfreq(len(pressure), 1.0 / sample_rate)
    a_signal = np.fft.irfft(spec * _a_weighting(freq), n=len(pressure))
    a_peak = float(np.abs(a_signal).max())

    def to_db(x: float) -> float:
        return 20.0 * np.log10(x / P_REF) if x > 0 else 0.0

    return {
        "peak_spl": to_db(peak),
        "rms_spl": to_db(rms),
        "peak_dba": to_db(a_peak),
    }


def voxelise_torso(torso: TorsoMesh, cfg: BodyFEMConfig) -> tuple[np.ndarray, np.ndarray]:
    """Voxelise the torso volume into a tetrahedral mesh.

    The torso is filled to its convex hull (it is convex-barrel-like) and
    the hull volume is diced into a regular voxel grid; every voxel cube
    inside the hull is split into six tetrahedra. Returns node coordinates
    and the tet connectivity.
    """
    h = cfg.voxel_size
    hull = Delaunay(torso.points[ConvexHull(torso.points).vertices])
    lo, hi = torso.points.min(axis=0), torso.points.max(axis=0)
    gx, gy, gz = (np.arange(lo[d], hi[d] + h, h) for d in range(3))
    nx, ny, nz = len(gx) - 1, len(gy) - 1, len(gz) - 1

    centres = np.array([
        [(gx[i] + gx[i + 1]) / 2, (gy[j] + gy[j + 1]) / 2, (gz[k] + gz[k + 1]) / 2]
        for i in range(nx) for j in range(ny) for k in range(nz)
    ])
    inside = (hull.find_simplex(centres) >= 0).reshape(nx, ny, nz)

    node_id: dict[tuple[int, int, int], int] = {}
    nodes: list[tuple[float, float, float]] = []

    def nid(i: int, j: int, k: int) -> int:
        key = (i, j, k)
        if key not in node_id:
            node_id[key] = len(nodes)
            nodes.append((gx[i], gy[j], gz[k]))
        return node_id[key]

    tets: list[tuple[int, int, int, int]] = []
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                if not inside[i, j, k]:
                    continue
                corner = [nid(i + di, j + dj, k + dk) for di, dj, dk in _CORNERS]
                for a, b, c, d in _TET6:
                    tets.append((corner[a], corner[b], corner[c], corner[d]))

    nodes_arr = np.array(nodes)
    tets_arr = np.array(tets)
    # orient every tetrahedron to a positive volume
    v = nodes_arr[tets_arr]
    signed = np.einsum(
        "ij,ij->i", v[:, 1] - v[:, 0], np.cross(v[:, 2] - v[:, 0], v[:, 3] - v[:, 0])
    )
    flip = signed < 0
    tets_arr[flip] = tets_arr[flip][:, [0, 1, 3, 2]]
    return nodes_arr, tets_arr


def _tet_volumes(nodes: np.ndarray, tets: np.ndarray) -> np.ndarray:
    """Volume of every tetrahedron."""
    v = nodes[tets]
    return np.abs(np.einsum(
        "ij,ij->i", v[:, 1] - v[:, 0], np.cross(v[:, 2] - v[:, 0], v[:, 3] - v[:, 0])
    )) / 6.0


def _modal_volume_velocity(
    nodes: np.ndarray, tets: np.ndarray, shape: np.ndarray
) -> float:
    """Net volume velocity of one mode - the air its deforming surface
    pushes. The divergence of the displacement field integrated over the
    torso; the divergence theorem makes it the surface flux ``oint phi.n dA``,
    the volume of air the chest wall sweeps per unit modal amplitude."""
    d = nodes[tets[:, 1:]] - nodes[tets[:, [0]]]  # (T, 3, 3) edge vectors
    u = shape[tets[:, 1:]] - shape[tets[:, [0]]]  # (T, 3, 3) displacement differences
    grad = np.linalg.solve(d, u)  # (T, 3, 3) displacement gradient per tet
    divergence = np.einsum("tii->t", grad)
    return float(np.sum(_tet_volumes(nodes, tets) * divergence))


def assemble_fem(
    nodes: np.ndarray, tets: np.ndarray, cfg: BodyFEMConfig
):
    """Assemble the 3D linear-elastic stiffness and consistent mass matrix."""
    mesh = MeshTet(nodes.T, tets.T)
    basis = Basis(mesh, ElementVector(ElementTetP1()))
    stiffness = linear_elasticity(*lame_parameters(cfg.youngs_modulus, cfg.poisson))
    k = stiffness.assemble(basis)

    @BilinearForm
    def mass(u, v, w):
        return cfg.density * dot(u, v)

    m = mass.assemble(basis)
    return k, m


def solve_modes(nodes: np.ndarray, tets: np.ndarray, cfg: BodyFEMConfig) -> TorsoFEM:
    """Solve the torso's elastic deformation modes.

    A free-free 3D body has six rigid-body modes at zero frequency; these
    are discarded and the next ``n_modes`` elastic modes are returned, with
    their nodal mode shapes and volume-velocity coefficients.
    """
    k, m = assemble_fem(nodes, tets, cfg)
    vals, vecs = eigsh(k, M=m, k=cfg.n_modes + 6, sigma=1e-3, which="LM")
    order = np.argsort(vals)
    vals, vecs = vals[order][6:], vecs[:, order][:, 6:]
    freqs = np.sqrt(np.abs(vals)) / (2.0 * np.pi)
    shapes = np.array([vecs[:, i].reshape(-1, 3) for i in range(cfg.n_modes)])
    vol_vel = np.array([_modal_volume_velocity(nodes, tets, s) for s in shapes])
    return TorsoFEM(
        nodes=nodes,
        tets=tets,
        frequencies=freqs,
        shapes=shapes,
        volume_velocity=vol_vel,
    )


def _impact_patch(nodes: np.ndarray, tets: np.ndarray) -> np.ndarray:
    """Boundary nodes of the back-side contact patch.

    The torso's shallowest axis is anterior-posterior; the back is its
    low-y face. The patch is the boundary band there, the scapular region
    that met the wall.
    """
    faces = np.sort(np.concatenate([
        tets[:, [0, 1, 2]], tets[:, [0, 1, 3]], tets[:, [0, 2, 3]], tets[:, [1, 2, 3]]
    ]), axis=1)
    uniq, counts = np.unique(faces, axis=0, return_counts=True)
    boundary_nodes = np.unique(uniq[counts == 1])
    y = nodes[:, 1]
    z = nodes[:, 2]
    back = y[boundary_nodes] <= y.min() + 0.05
    z_lo, z_hi = z.min(), z.max()
    mid = (z[boundary_nodes] >= z_lo + 0.2 * (z_hi - z_lo)) & (
        z[boundary_nodes] <= z_lo + 0.8 * (z_hi - z_lo)
    )
    return boundary_nodes[back & mid]


def _modal_response(
    freq: float, zeta: float, gamma: float, t: np.ndarray, force: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Displacement and acceleration of one damped modal oscillator under
    the contact forcing ``gamma * force(t)``."""
    omega = 2.0 * np.pi * freq
    system = (
        np.array([[0.0, 1.0], [-(omega**2), -2.0 * zeta * omega]]),
        np.array([[0.0], [1.0]]),
        np.array([[1.0, 0.0], [0.0, 1.0]]),
        np.zeros((2, 1)),
    )
    _, y, _ = lsim(system, gamma * force, t)
    q, qdot = y[:, 0], y[:, 1]
    qddot = gamma * force - 2.0 * zeta * omega * qdot - omega**2 * q
    return q, qddot


def _surface_roughness(t: np.ndarray, cfg: BodyFEMConfig) -> np.ndarray:
    """The texture the uneven body surface adds to the contact force.

    The body surface is not smooth - ribs, the spine and clothing folds of
    centimetre scale engage the wall bump by bump as the body presses in.
    At the closing velocity that engagement modulates the contact force in
    a band set by the bump spacing (roughly 1-10 cm). Returns a zero-mean
    band-passed modulation of unit RMS, scaled by ``surface_roughness``.
    """
    rng = np.random.default_rng(cfg.roughness_seed)
    nyquist = 0.5 * cfg.sample_rate
    lo = cfg.v_close / 0.10  # 10 cm bumps - the low edge of the engagement band
    hi = cfg.v_close / 0.01  # 1 cm bumps - the high edge
    sos = butter(4, [lo / nyquist, hi / nyquist], btype="band", output="sos")
    rough = sosfiltfilt(sos, rng.standard_normal(len(t)))
    return cfg.surface_roughness * rough / rough.std()


def impact_response(
    fem: TorsoFEM, cfg: BodyFEMConfig
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Modal response of the torso to the back-impact contact pulse.

    The contact force - the body's deceleration carried by the effective
    impacting mass, grained by the uneven body surface - is projected onto
    every deformation mode at the back contact patch, and each mode is
    time-marched as a damped oscillator. Returns the time base, the modal
    displacement and acceleration histories, and the contact force pulse
    that drove them.
    """
    t, accel = deceleration_pulse(cfg)
    # the uneven body surface grains the contact force
    force = cfg.m_eff * accel * np.clip(1.0 + _surface_roughness(t, cfg), 0.0, None)

    # project the contact load onto each mode to drive its squash
    patch = _impact_patch(fem.nodes, fem.tets)
    modal_q = np.zeros((cfg.n_modes, len(t)))
    modal_a = np.zeros((cfg.n_modes, len(t)))
    for i in range(cfg.n_modes):
        gamma = float(np.mean(fem.shapes[i][patch, 1]))  # patch participation, y-axis
        modal_q[i], modal_a[i] = _modal_response(
            fem.frequencies[i], cfg.modal_damping, gamma, t, force
        )
    return t, modal_q, modal_a, force


def radiate_modes(
    fem: TorsoFEM, t: np.ndarray, modal_accel: np.ndarray, cfg: BodyFEMConfig
) -> np.ndarray:
    """Far-field pressure at the microphone - the air the body pushed.

    The body is not a source; only the air displaced by its deforming
    surface radiates. Each mode's surface sweeps a volume of air set by its
    volume-velocity coefficient; the pushed air is a compact monopole, and
    the pressure is ``rho / (2 pi r)`` - the rigid wall baffles it into a
    half-space - times the summed volume acceleration, delayed by the
    propagation time."""
    volume_accel = np.zeros_like(t)
    for i in range(cfg.n_modes):
        volume_accel += fem.volume_velocity[i] * modal_accel[i]
    pressure = cfg.air_rho / (2.0 * np.pi * cfg.mic_distance) * volume_accel
    shift = int(round(cfg.mic_distance / cfg.air_c * cfg.sample_rate))
    return np.roll(pressure, shift)


def air_escape(cfg: BodyFEMConfig) -> tuple[np.ndarray, np.ndarray]:
    """Sound of the air squeezed out of the closing wall-body gap.

    As the body's back nears the wall the trapped air is forced out
    through the patch perimeter. The escape velocity climbs as the gap
    thins - ``v_esc = A v_close / (P h(t))`` - and peaks the instant the
    gap seals, the "thud". The body surface is uneven, so the gap is
    non-uniform and the escaping flow is turbulent: the sound is a brief,
    broadband, textured burst, far higher in frequency than the body's
    thump. The far-field pressure follows a compact aeroacoustic scaling,
    ``rho A v_close / (4 pi r^2 c) * v_esc^2``, modulated by band-passed
    noise that carries the surface texture. It is an order-of-magnitude
    aeroacoustic estimate, not a resolved flow solution.
    """
    n = int(cfg.t_max * cfg.sample_rate)
    t = np.arange(n) / cfg.sample_rate
    perimeter = 2.0 * np.sqrt(np.pi * cfg.contact_patch_area)

    # the gap closes at the closing velocity until the uneven surface seals it
    gap = cfg.gap_squeeze_start - cfg.v_close * t
    squeezing = gap > cfg.gap_seal
    gap = np.clip(gap, cfg.gap_seal, None)
    v_esc = cfg.contact_patch_area * cfg.v_close / (perimeter * gap)
    v_esc[~squeezing] = 0.0  # the gap is sealed - the escape is over

    # the uneven body surface makes the escape turbulent - a broadband texture
    rng = np.random.default_rng(cfg.escape_seed)
    nyquist = 0.5 * cfg.sample_rate
    sos = butter(
        4, [cfg.escape_band_lo / nyquist, cfg.escape_band_hi / nyquist],
        btype="band", output="sos",
    )
    texture = sosfiltfilt(sos, rng.standard_normal(n))
    texture /= texture.std()  # unit RMS - the v_esc^2 envelope sets the level

    prefactor = (
        cfg.air_rho * cfg.contact_patch_area * cfg.v_close
        / (4.0 * np.pi * cfg.mic_distance**2 * cfg.air_c)
    )
    pressure = prefactor * v_esc**2 * texture
    shift = int(round(cfg.mic_distance / cfg.air_c * cfg.sample_rate))
    return t, np.roll(pressure, shift)


def solve_body_fem(cfg: BodyFEMConfig | None = None) -> BodyFEMResult:
    """Solve the FEM body-impact sound - the torso deforms and pushes air
    (the low thump), the closing gap squeezes air out (the high textured
    burst), and the two sum at the microphone."""
    if cfg is None:
        cfg = BodyFEMConfig()

    points, triangles = load_body_mesh(cfg)
    torso = isolate_upper_torso(points, triangles, cfg)
    nodes, tets = voxelise_torso(torso, cfg)
    fem = solve_modes(nodes, tets, cfg)
    t, modal_q, modal_a, _ = impact_response(fem, cfg)
    pressure_thump = radiate_modes(fem, t, modal_a, cfg)
    _, pressure_escape = air_escape(cfg)
    pressure = pressure_thump + pressure_escape

    # peak deformation - reconstruct the displacement field at strided steps
    stride = max(1, len(t) // 400)
    disp = np.einsum("it,inj->tnj", modal_q[:, ::stride], fem.shapes)
    deflection = float(np.linalg.norm(disp, axis=2).max())
    return BodyFEMResult(
        config=cfg,
        torso=torso,
        fem=fem,
        t=t,
        modal_amplitude=modal_q,
        surface_deflection=deflection,
        pressure_thump=pressure_thump,
        pressure_escape=pressure_escape,
        pressure=pressure,
        peak_spl=peak_spl(pressure),
    )


__all__ = [
    "P_REF",
    "BodyFEMConfig",
    "BodyFEMResult",
    "TorsoFEM",
    "TorsoMesh",
    "air_escape",
    "assemble_fem",
    "deceleration_pulse",
    "impact_response",
    "isolate_upper_torso",
    "load_body_mesh",
    "peak_spl",
    "radiate_modes",
    "solve_body_fem",
    "solve_modes",
    "sound_levels",
    "voxelise_torso",
]
