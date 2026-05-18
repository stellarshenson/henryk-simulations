"""FEM door-impact sound - the steel door box rings, the clang.

Notebook 04's model. When the body strikes the elevator door the steel
leaf is set ringing, and its flexural vibration radiates to a microphone
1 m away as the metallic "clang". This module models the door alone - not
the body, not the air the body pushes (that is notebook 03).

The ZREMB DT37/1 leaf is not a flat sheet: it is a welded steel box - two
2 mm skins spaced 51 mm apart, tied by a perimeter frame, with a tall
narrow wired-glass vision window. That box is what makes the door stiff,
so it *clangs* rather than booms. The actual box is built and tessellated:
the steel volume (the two skins, the frame, the window surround) is
voxelised into a tetrahedral solid the same way the torso was, scikit-fem
assembles its 3D linear-elastic stiffness and mass, and an eigensolve
gives the leaf's flexural modes - hundreds of hertz upward.

The impact excites the modes at the strike point; modal damping settles
the ring (the sound dampening); and the room-side skin, the door's
radiating face, pushes air to the microphone.

Pipeline: ``voxelise_door`` -> ``assemble_fem`` -> ``solve_door_modes`` ->
``impact_response`` -> ``radiate``. ``solve_door_sound`` runs the chain.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.signal import lsim
from scipy.sparse.linalg import eigsh
from skfem import Basis, BilinearForm, ElementTetP1, ElementVector, MeshTet
from skfem.helpers import dot
from skfem.models.elasticity import lame_parameters, linear_elasticity

from henryk_simulations.corridor.bodyfem import peak_spl

# the six tetrahedra of a voxel cube, sharing the 0-7 space diagonal
_TET6 = ((0, 7, 1, 3), (0, 7, 3, 2), (0, 7, 2, 6), (0, 7, 6, 4), (0, 7, 4, 5), (0, 7, 5, 1))
_CORNERS = ((0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0),
            (0, 0, 1), (1, 0, 1), (0, 1, 1), (1, 1, 1))


@dataclass(frozen=True)
class DoorFEMConfig:
    """Configuration for the FEM door-impact sound model (ZREMB DT37/1)."""

    # door box geometry - the welded steel leaf
    panel_width: float = 1.0  # m
    panel_height: float = 2.0  # m
    skin_thickness: float = 0.002  # m, steel plate (skin) thickness
    cavity_gap: float = 0.025  # m, the air cavity between the two steel skins
    frame_width: float = 0.04  # m, welded perimeter/window frame rail
    # window cutout - the wired-glass vision panel (a hole in the steel)
    window_width: float = 0.15  # m
    window_height: float = 1.2  # m
    window_cx: float = 0.5  # m, window centre, width axis
    window_cy: float = 1.1  # m, window centre, height axis
    # steel
    youngs_modulus: float = 200e9  # Pa
    poisson: float = 0.30
    density: float = 7850.0  # kg/m^3
    # finite-element model
    voxel_size: float = 0.025  # m, in-plane voxel edge
    n_modes: int = 30  # elastic flexural modes retained
    modal_damping: float = 0.02  # framed-steel-leaf loss factor (the sound dampening)
    # impact - the body delivered to the door by notebook 02's corridor model
    peak_force: float = 6000.0  # N, peak contact force
    contact_time: float = 0.030  # s
    strike_x: float = 0.65  # m, strike point, width axis - right of the door centre
    strike_y: float = 1.3  # m, strike point - the upper-back contact height
    # acoustics
    air_rho: float = 1.2  # kg/m^3
    air_c: float = 343.0  # m/s
    mic_distance: float = 1.0  # m
    sample_rate: int = 44100  # Hz
    t_max: float = 0.60  # s, output window - the steel rings on

    @property
    def leaf_depth(self) -> float:
        """Overall leaf depth - the air cavity plus the two steel skins."""
        return self.cavity_gap + 2.0 * self.skin_thickness


@dataclass(frozen=True)
class DoorFEM:
    """The voxelised steel door box and its solved flexural modes."""

    nodes: np.ndarray  # (N, 3) m
    tets: np.ndarray  # (T, 4) int
    frequencies: np.ndarray  # (n_modes,) Hz
    shapes: np.ndarray  # (n_modes, N, 3) nodal mode shapes
    volume_velocity: np.ndarray  # (n_modes,) m^3 - effective radiating volume velocity
    radiation_efficiency: np.ndarray  # (n_modes,) sub-critical panel radiation efficiency
    strike_participation: np.ndarray  # (n_modes,) mode shape at the strike point


@dataclass(frozen=True)
class DoorFEMResult:
    """Solved FEM door-impact sound at the microphone."""

    config: DoorFEMConfig
    fem: DoorFEM
    t: np.ndarray  # s
    force: np.ndarray  # N, contact force pulse
    modal_amplitude: np.ndarray  # (n_modes, n_t) modal displacement q_i(t)
    pressure: np.ndarray  # Pa, sound pressure at the microphone
    peak_spl: float  # dB SPL


def voxelise_door(cfg: DoorFEMConfig) -> tuple[np.ndarray, np.ndarray]:
    """Tessellate the steel door box into a tetrahedral solid.

    The box is diced into a voxel grid - uniform in the panel plane, three
    layers through the depth (front skin, hollow core, back skin). A voxel
    is steel where it belongs to a skin (everywhere but the window hole) or
    to the perimeter frame or window surround (which fill the core and tie
    the two skins). Every steel voxel becomes six tetrahedra.
    """
    width, height, depth = cfg.panel_width, cfg.panel_height, cfg.leaf_depth
    skin, frame = cfg.skin_thickness, cfg.frame_width
    h = cfg.voxel_size
    gx = np.linspace(0.0, width, round(width / h) + 1)
    gy = np.linspace(0.0, height, round(height / h) + 1)
    gz = np.array([0.0, skin, depth - skin, depth])  # front skin / core / back skin
    nx, ny, nz = len(gx) - 1, len(gy) - 1, len(gz) - 1

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
        cx = (gx[i] + gx[i + 1]) / 2.0
        for j in range(ny):
            cy = (gy[j] + gy[j + 1]) / 2.0
            in_hole = (
                abs(cx - cfg.window_cx) < cfg.window_width / 2.0
                and abs(cy - cfg.window_cy) < cfg.window_height / 2.0
            )
            in_surround = (
                abs(cx - cfg.window_cx) < cfg.window_width / 2.0 + frame
                and abs(cy - cfg.window_cy) < cfg.window_height / 2.0 + frame
            ) and not in_hole
            in_frame = (
                cx < frame or cx > width - frame or cy < frame or cy > height - frame
            )
            for k in range(nz):
                steel = (not in_hole) if k in (0, 2) else (in_frame or in_surround)
                if not steel:
                    continue
                corner = [nid(i + di, j + dj, k + dk) for di, dj, dk in _CORNERS]
                for a, b, c, d in _TET6:
                    tets.append((corner[a], corner[b], corner[c], corner[d]))

    nodes_arr = np.array(nodes)
    tets_arr = np.array(tets)
    v = nodes_arr[tets_arr]
    signed = np.einsum(
        "ij,ij->i", v[:, 1] - v[:, 0], np.cross(v[:, 2] - v[:, 0], v[:, 3] - v[:, 0])
    )
    flip = signed < 0
    tets_arr[flip] = tets_arr[flip][:, [0, 1, 3, 2]]
    return nodes_arr, tets_arr


def _critical_frequency(cfg: DoorFEMConfig) -> float:
    """Steel-skin coincidence frequency - above it the panel radiates fully."""
    return (
        cfg.air_c**2
        / (2.0 * np.pi)
        * np.sqrt(12.0 * cfg.density * (1.0 - cfg.poisson**2) / cfg.youngs_modulus)
        / cfg.skin_thickness
    )


def assemble_fem(nodes: np.ndarray, tets: np.ndarray, cfg: DoorFEMConfig):
    """Assemble the 3D linear-elastic stiffness and consistent mass matrix."""
    mesh = MeshTet(nodes.T, tets.T)
    basis = Basis(mesh, ElementVector(ElementTetP1()))
    stiffness = linear_elasticity(*lame_parameters(cfg.youngs_modulus, cfg.poisson))
    k = stiffness.assemble(basis)

    @BilinearForm
    def mass(u, v, w):
        return cfg.density * dot(u, v)

    return k, mass.assemble(basis)


def solve_door_modes(cfg: DoorFEMConfig) -> DoorFEM:
    """Solve the steel door box's flexural modes.

    The leaf is free-free: the six rigid-body modes are discarded and the
    next ``n_modes`` elastic modes returned. Each mode carries its
    volume-velocity coefficient - the air the room-side skin pushes - and
    its participation at the strike point.
    """
    nodes, tets = voxelise_door(cfg)
    k, m = assemble_fem(nodes, tets, cfg)
    vals, vecs = eigsh(k, M=m, k=cfg.n_modes + 6, sigma=1.0, which="LM")
    order = np.argsort(vals)
    vals, vecs = vals[order][6:], vecs[:, order][:, 6:]
    freqs = np.sqrt(np.abs(vals)) / (2.0 * np.pi)
    shapes = np.array([vecs[:, i].reshape(-1, 3) for i in range(cfg.n_modes)])

    # the room-side skin radiates. A flexing panel's net volume velocity
    # nearly cancels (the modal lobes are +/-), but the panel still radiates
    # through sub-critical edge radiation: each mode carries an efficiency
    # sigma < 1 below the steel coincidence frequency, and its effective
    # volume velocity is the RMS of the face's normal motion (which does not
    # cancel) times the face area, weighted by sqrt(sigma).
    back = np.isclose(nodes[:, 2], cfg.leaf_depth)
    face_area = cfg.panel_width * cfg.panel_height - cfg.window_width * cfg.window_height
    efficiency = np.minimum(1.0, np.sqrt(freqs / _critical_frequency(cfg)))
    face_rms = np.array([
        np.sqrt(np.mean(shapes[i][back, 2] ** 2)) for i in range(cfg.n_modes)
    ])
    vol_vel = np.sqrt(efficiency) * face_area * face_rms

    # the impact lands on the front skin at the strike point
    front = np.isclose(nodes[:, 2], 0.0)
    front_idx = np.where(front)[0]
    strike = np.array([cfg.strike_x, cfg.strike_y])
    nearest = front_idx[np.argmin(np.linalg.norm(nodes[front_idx, :2] - strike, axis=1))]
    strike_part = shapes[:, nearest, 2]

    return DoorFEM(
        nodes=nodes,
        tets=tets,
        frequencies=freqs,
        shapes=shapes,
        volume_velocity=vol_vel,
        radiation_efficiency=efficiency,
        strike_participation=strike_part,
    )


def contact_pulse(cfg: DoorFEMConfig) -> tuple[np.ndarray, np.ndarray]:
    """The impact contact force - a smooth sine-squared pulse on the door."""
    n = int(cfg.t_max * cfg.sample_rate)
    t = np.arange(n) / cfg.sample_rate
    force = np.zeros(n)
    inside = t < cfg.contact_time
    force[inside] = cfg.peak_force * np.sin(np.pi * t[inside] / cfg.contact_time) ** 2
    return t, force


def impact_response(
    fem: DoorFEM, cfg: DoorFEMConfig
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Modal response of the door to the impact contact pulse.

    The contact force, applied at the strike point, is projected onto each
    flexural mode and drives a damped modal oscillator. Returns the time
    base, the modal displacement and acceleration histories, and the
    contact force.
    """
    t, force = contact_pulse(cfg)
    omega = 2.0 * np.pi * fem.frequencies
    modal_q = np.zeros((cfg.n_modes, len(t)))
    modal_a = np.zeros((cfg.n_modes, len(t)))
    for i in range(cfg.n_modes):
        w_n, gamma = omega[i], fem.strike_participation[i]
        system = (
            np.array([[0.0, 1.0], [-(w_n**2), -2.0 * cfg.modal_damping * w_n]]),
            np.array([[0.0], [1.0]]),
            np.array([[1.0, 0.0], [0.0, 1.0]]),
            np.zeros((2, 1)),
        )
        _, y, _ = lsim(system, gamma * force, t)
        q, qdot = y[:, 0], y[:, 1]
        modal_q[i] = q
        modal_a[i] = gamma * force - 2.0 * cfg.modal_damping * w_n * qdot - w_n**2 * q
    return t, modal_q, modal_a, force


def radiate(
    fem: DoorFEM, t: np.ndarray, modal_accel: np.ndarray, cfg: DoorFEMConfig
) -> np.ndarray:
    """Far-field pressure at the microphone - the air the door's face pushed.

    The leaf is set in the wall, so its room-side skin radiates as a
    baffled compact monopole: the pressure is ``rho / (2 pi r)`` times the
    summed modal volume acceleration, delayed by the propagation time.
    """
    volume_accel = np.zeros_like(t)
    for i in range(cfg.n_modes):
        volume_accel += fem.volume_velocity[i] * modal_accel[i]
    pressure = cfg.air_rho / (2.0 * np.pi * cfg.mic_distance) * volume_accel
    shift = int(round(cfg.mic_distance / cfg.air_c * cfg.sample_rate))
    return np.roll(pressure, shift)


def solve_door_sound(cfg: DoorFEMConfig | None = None) -> DoorFEMResult:
    """Solve the FEM door-impact sound - the steel leaf rings, the clang
    reaches the microphone."""
    if cfg is None:
        cfg = DoorFEMConfig()
    fem = solve_door_modes(cfg)
    t, modal_q, modal_a, force = impact_response(fem, cfg)
    pressure = radiate(fem, t, modal_a, cfg)
    return DoorFEMResult(
        config=cfg,
        fem=fem,
        t=t,
        force=force,
        modal_amplitude=modal_q,
        pressure=pressure,
        peak_spl=peak_spl(pressure),
    )


__all__ = [
    "DoorFEM",
    "DoorFEMConfig",
    "DoorFEMResult",
    "assemble_fem",
    "contact_pulse",
    "impact_response",
    "radiate",
    "solve_door_modes",
    "solve_door_sound",
    "voxelise_door",
]
