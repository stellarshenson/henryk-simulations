"""Guards for the FEM body-impact sound model."""

from __future__ import annotations

import numpy as np
import pytest

from henryk_simulations.corridor.bodyfem import (
    BodyFEMConfig,
    _surface_roughness,
    air_escape,
    boundary_facets,
    deceleration_pulse,
    decimate_mesh,
    ensure_body_mesh,
    isolate_upper_torso,
    load_body_mesh,
    peak_spl,
    solve_body_fem,
    solve_modes,
    sound_levels,
    tet_mesh_volume,
    voxelise_torso,
    write_listening_wav,
)


@pytest.fixture(scope="module")
def cfg() -> BodyFEMConfig:
    return BodyFEMConfig()


@pytest.fixture(scope="module")
def body(cfg):
    return load_body_mesh(cfg)


@pytest.fixture(scope="module")
def torso(cfg, body):
    points, triangles = body
    return isolate_upper_torso(points, triangles, cfg)


@pytest.fixture(scope="module")
def voxel(cfg, torso):
    return voxelise_torso(torso, cfg)


@pytest.fixture(scope="module")
def fem(cfg, voxel):
    nodes, tets = voxel
    return solve_modes(nodes, tets, cfg)


@pytest.fixture(scope="module")
def result(cfg):
    return solve_body_fem(cfg)


def _spectral_centroid(signal: np.ndarray, sample_rate: int) -> float:
    spec = np.abs(np.fft.rfft(signal))
    freq = np.fft.rfftfreq(len(signal), 1.0 / sample_rate)
    return float(np.sum(freq * spec) / np.sum(spec))


# ---------------------------------------------------------------------------
# Body mesh and torso isolation
# ---------------------------------------------------------------------------


def test_body_mesh_loads(body) -> None:
    points, triangles = body
    assert points.shape[1] == 3
    assert triangles.shape[1] == 3
    assert len(points) > 100
    assert int(triangles.max()) < len(points)


def test_torso_is_a_subset_of_the_body(body, torso) -> None:
    points, triangles = body
    assert 0 < len(torso.points) < len(points)
    assert 0 < len(torso.triangles) < len(triangles)


def test_torso_lies_in_the_isolation_band(cfg, body, torso) -> None:
    points, _ = body
    z = points[:, 2]
    height = z.max() - z.min()
    band_lo = z.min() + cfg.torso_z_lo_frac * height
    band_hi = z.min() + cfg.torso_z_hi_frac * height
    tz = torso.points[:, 2]
    assert tz.min() >= band_lo - 1e-6
    assert tz.max() <= band_hi + 1e-6


def test_torso_volume_is_physical(torso) -> None:
    # an adult upper torso - roughly 10-40 L
    assert 0.010 < torso.volume < 0.040


def test_decimate_mesh_reduces_and_stays_valid(body) -> None:
    # vertex clustering at a coarser grid reduces the mesh, indices stay valid
    points, triangles = body
    dp, dt = decimate_mesh(points, triangles, 0.08)
    assert 0 < len(dp) < len(points)
    assert len(dt) > 0
    assert int(dt.max()) < len(dp)
    assert np.all(np.isfinite(dp))


def test_ensure_body_mesh_returns_the_working_mesh(cfg) -> None:
    # the working mesh is committed - ensure_body_mesh is a no-op, returns it
    path = ensure_body_mesh(cfg)
    assert path.exists()
    assert path.suffix == ".obj"


# ---------------------------------------------------------------------------
# Deceleration pulse
# ---------------------------------------------------------------------------


def test_pulse_is_non_negative_and_bounded(cfg) -> None:
    t, a = deceleration_pulse(cfg)
    assert np.all(a >= 0.0)
    assert np.all(np.isfinite(a))
    assert np.all(a[t >= cfg.contact_time] == 0.0)


def test_pulse_impulse_matches_velocity_change(cfg) -> None:
    t, a = deceleration_pulse(cfg)
    impulse = np.trapezoid(a, t)
    expected = cfg.v_close * (1.0 + cfg.restitution)
    assert impulse == pytest.approx(expected, rel=0.02)


# ---------------------------------------------------------------------------
# Voxelisation
# ---------------------------------------------------------------------------


def test_voxelise_produces_tet_mesh(voxel) -> None:
    nodes, tets = voxel
    assert nodes.shape[1] == 3
    assert tets.shape[1] == 4
    assert len(nodes) > 100
    assert len(tets) > 100


def test_tet_indices_valid(voxel) -> None:
    nodes, tets = voxel
    assert int(tets.max()) < len(nodes)
    assert int(tets.min()) >= 0


def test_tets_have_positive_volume(voxel) -> None:
    nodes, tets = voxel
    v = nodes[tets]
    signed = np.einsum(
        "ij,ij->i", v[:, 1] - v[:, 0], np.cross(v[:, 2] - v[:, 0], v[:, 3] - v[:, 0])
    )
    assert np.all(signed > 0)


def test_tet_nodes_within_torso_bounds(cfg, torso, voxel) -> None:
    nodes, _ = voxel
    lo, hi = torso.points.min(axis=0), torso.points.max(axis=0)
    assert np.all(nodes >= lo - cfg.voxel_size)
    assert np.all(nodes <= hi + cfg.voxel_size)


# ---------------------------------------------------------------------------
# FEM deformation modes
# ---------------------------------------------------------------------------


def test_modes_count(fem, cfg) -> None:
    assert len(fem.frequencies) == cfg.n_modes
    assert fem.shapes.shape == (cfg.n_modes, len(fem.nodes), 3)


def test_modes_ascending_and_positive(fem) -> None:
    assert np.all(fem.frequencies > 0.0)
    assert np.all(np.diff(fem.frequencies) >= -1e-6)


def test_modes_in_soft_tissue_band(fem) -> None:
    # rigid-body modes discarded; elastic modes sit in the tens-of-hertz band
    assert fem.frequencies[0] > 1.0
    assert fem.frequencies[-1] < 500.0


def test_compressible_thorax_pushes_air(fem) -> None:
    # an air-filled (compressible) thorax has modes with real volume velocity
    assert np.all(np.isfinite(fem.volume_velocity))
    assert np.abs(fem.volume_velocity).max() > 0.0


# ---------------------------------------------------------------------------
# Impact response, radiation and the air-escape burst
# ---------------------------------------------------------------------------


def test_modal_amplitude_finite(result, cfg) -> None:
    assert result.modal_amplitude.shape[0] == cfg.n_modes
    assert result.modal_amplitude.shape[1] == len(result.t)
    assert np.all(np.isfinite(result.modal_amplitude))


def test_pressure_components_sum_to_total(result) -> None:
    for sig in (result.pressure_thump, result.pressure_escape, result.pressure):
        assert sig.shape == result.t.shape
        assert np.all(np.isfinite(sig))
    np.testing.assert_allclose(
        result.pressure, result.pressure_thump + result.pressure_escape
    )


def test_peak_spl_in_plausible_band(result) -> None:
    assert np.isfinite(result.peak_spl)
    assert 40.0 < result.peak_spl < 140.0


def test_chest_deflection_is_a_squash(result) -> None:
    # the chest compresses on impact - a few cm, not an absurd value
    assert result.surface_deflection > 0.0
    assert result.surface_deflection < 0.10


def test_air_escape_is_a_localised_burst(cfg) -> None:
    t, pressure = air_escape(cfg)
    assert pressure.shape == t.shape
    assert np.all(np.isfinite(pressure))
    assert np.abs(pressure).max() > 0.0
    # the gap seals within a few ms - the escape is over long before t_max
    nonzero = np.abs(pressure) > 0.0
    assert nonzero.sum() < 0.1 * len(pressure)


def test_air_escape_is_higher_frequency_than_the_thump(result, cfg) -> None:
    # the squeezed-air burst is broadband and far higher in pitch than the thump
    thump_centroid = _spectral_centroid(result.pressure_thump, cfg.sample_rate)
    escape_centroid = _spectral_centroid(result.pressure_escape, cfg.sample_rate)
    assert escape_centroid > 5.0 * thump_centroid


def test_surface_roughness_grains_the_contact(cfg) -> None:
    # the uneven body surface is a zero-mean, unit-RMS-scaled force modulation
    t, _ = deceleration_pulse(cfg)
    rough = _surface_roughness(t, cfg)
    assert np.all(np.isfinite(rough))
    assert abs(rough.mean()) < 0.05
    assert rough.std() == pytest.approx(cfg.surface_roughness, rel=0.05)


# ---------------------------------------------------------------------------
# Sound levels
# ---------------------------------------------------------------------------


def test_sound_levels_finite_and_a_weighting_cuts_the_thump(result, cfg) -> None:
    levels = sound_levels(result.pressure, cfg.sample_rate)
    assert all(np.isfinite(v) for v in levels.values())
    # A-weighting heavily attenuates the sub-bass thump, so dBA sits well below peak
    thump = sound_levels(result.pressure_thump, cfg.sample_rate)
    assert thump["peak_dba"] < thump["peak_spl"] - 20.0


def test_peak_spl_zero_for_silence() -> None:
    assert peak_spl(np.zeros(100)) == 0.0


# ---------------------------------------------------------------------------
# Tet-mesh helpers - boundary facets and mesh volume
# ---------------------------------------------------------------------------


def test_boundary_facets_of_a_lone_tet() -> None:
    # a single tetrahedron has all four of its faces on the boundary
    facets = boundary_facets(np.array([[0, 1, 2, 3]]))
    assert facets.shape == (4, 3)


def test_boundary_facets_drop_a_shared_face() -> None:
    # two tets sharing the (0, 1, 2) face - that face is interior, six remain
    facets = boundary_facets(np.array([[0, 1, 2, 3], [0, 1, 2, 4]]))
    assert facets.shape == (6, 3)
    assert not any(tuple(f) == (0, 1, 2) for f in facets)


def test_boundary_facets_of_the_torso_are_valid(voxel) -> None:
    nodes, tets = voxel
    facets = boundary_facets(tets)
    assert facets.shape[1] == 3
    assert len(facets) > 0
    assert int(facets.min()) >= 0
    assert int(facets.max()) < len(nodes)
    assert np.all(np.diff(facets, axis=1) > 0)  # every row sorted ascending


def test_tet_mesh_volume_of_a_unit_tet() -> None:
    nodes = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    assert tet_mesh_volume(nodes, np.array([[0, 1, 2, 3]])) == pytest.approx(1.0 / 6.0)


def test_tet_mesh_volume_of_the_torso_is_physical(voxel) -> None:
    nodes, tets = voxel
    vol = tet_mesh_volume(nodes, tets)
    assert np.isfinite(vol)
    assert 0.005 < vol < 0.080  # the voxelised upper torso, a few tens of litres


# ---------------------------------------------------------------------------
# Listening WAV export
# ---------------------------------------------------------------------------


def test_write_listening_wav_roundtrips(tmp_path) -> None:
    from scipy.io import wavfile

    sample_rate = 44100
    signal = np.sin(2.0 * np.pi * 200.0 * np.arange(sample_rate) / sample_rate)
    out = write_listening_wav(signal, tmp_path / "tone.wav", sample_rate, lead_in=0.5)
    assert out.exists()
    assert out.suffix == ".wav"
    rate, data = wavfile.read(out)
    assert rate == sample_rate
    assert data.dtype == np.int16
    # the silent lead-in is prepended to the signal
    assert len(data) == len(signal) + int(0.5 * sample_rate)
    # the tanh soft-clip holds the peak within the 0.97 headroom
    assert np.abs(data).max() <= int(0.97 * 32767) + 1
