"""Guards for the FEM door-impact sound model."""

from __future__ import annotations

import numpy as np
import pytest

from henryk_simulations.corridor.doorfem import (
    DoorFEMConfig,
    contact_pulse,
    solve_door_sound,
    voxelise_door,
)


@pytest.fixture(scope="module")
def cfg() -> DoorFEMConfig:
    return DoorFEMConfig()


@pytest.fixture(scope="module")
def voxel(cfg):
    return voxelise_door(cfg)


@pytest.fixture(scope="module")
def result(cfg):
    return solve_door_sound(cfg)


# ---------------------------------------------------------------------------
# Voxelised door box
# ---------------------------------------------------------------------------


def test_voxelise_produces_tet_mesh(voxel) -> None:
    nodes, tets = voxel
    assert nodes.shape[1] == 3
    assert tets.shape[1] == 4
    assert len(nodes) > 1000
    assert len(tets) > 1000


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


def test_door_box_within_bounds(cfg, voxel) -> None:
    nodes, _ = voxel
    assert nodes[:, 0].min() >= -1e-9
    assert nodes[:, 0].max() <= cfg.panel_width + 1e-9
    assert nodes[:, 1].max() <= cfg.panel_height + 1e-9
    assert nodes[:, 2].max() <= cfg.leaf_depth + 1e-9


def test_box_is_hollow(cfg, voxel) -> None:
    # the core layer is steel only at the frame - the box is mostly hollow
    nodes, _ = voxel
    z = nodes[:, 2]
    front = np.isclose(z, 0.0).sum()
    core = ((z > cfg.skin_thickness) & (z < cfg.leaf_depth - cfg.skin_thickness)).sum()
    assert core < front  # the hollow core has far fewer nodes than a skin


# ---------------------------------------------------------------------------
# Flexural modes
# ---------------------------------------------------------------------------


def test_modes_count(result, cfg) -> None:
    fem = result.fem
    assert len(fem.frequencies) == cfg.n_modes
    assert fem.shapes.shape == (cfg.n_modes, len(fem.nodes), 3)


def test_modes_ascending_and_positive(result) -> None:
    f = result.fem.frequencies
    assert np.all(f > 0.0)
    assert np.all(np.diff(f) >= -1e-6)


def test_door_is_stiff(result) -> None:
    # the welded box is stiff - the fundamental is well above a floppy
    # flat-sheet's ~11 Hz, in the tens-to-hundreds of hertz
    assert result.fem.frequencies[0] > 30.0
    assert result.fem.frequencies[-1] < 5000.0


def test_radiation_efficiency_sub_critical(result) -> None:
    sigma = result.fem.radiation_efficiency
    assert np.all(sigma > 0.0)
    assert np.all(sigma <= 1.0)


def test_volume_velocity_finite(result, cfg) -> None:
    vv = result.fem.volume_velocity
    assert vv.shape == (cfg.n_modes,)
    assert np.all(np.isfinite(vv))


# ---------------------------------------------------------------------------
# Impact pulse and the radiated clang
# ---------------------------------------------------------------------------


def test_contact_pulse_non_negative_and_bounded(cfg) -> None:
    t, force = contact_pulse(cfg)
    assert np.all(force >= 0.0)
    assert np.all(np.isfinite(force))
    assert np.all(force[t >= cfg.contact_time] == 0.0)
    assert force.max() == pytest.approx(cfg.peak_force, rel=0.01)


def test_modal_amplitude_finite(result, cfg) -> None:
    assert result.modal_amplitude.shape[0] == cfg.n_modes
    assert result.modal_amplitude.shape[1] == len(result.t)
    assert np.all(np.isfinite(result.modal_amplitude))


def test_pressure_finite(result) -> None:
    assert result.pressure.shape == result.t.shape
    assert np.all(np.isfinite(result.pressure))
    assert np.abs(result.pressure).max() > 0.0


def test_peak_spl_in_plausible_band(result) -> None:
    # a struck steel door - an audible metallic clang, not silent, not a gunshot
    assert 50.0 < result.peak_spl < 130.0
