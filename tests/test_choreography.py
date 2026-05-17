"""Guards for the structural decoupled-singularity choreography model.

These tests verify the simulation **obeys its constraints** (boundary
conditions, timeline, biomechanical production limits) and **produces no
artefacts** (discontinuities, spurious oscillation, non-physical values).
"""

from __future__ import annotations

import numpy as np
import pytest

from henryk_simulations.corridor import (
    ChoreographyConfig,
    constraints,
    free_parameters,
    solve_choreography,
)
from henryk_simulations.corridor.choreography import YIELD_FACTORS, impact_singularity


@pytest.fixture(scope="module")
def cfg() -> ChoreographyConfig:
    return ChoreographyConfig()


@pytest.fixture(scope="module")
def result():
    return solve_choreography()


# ---------------------------------------------------------------------------
# Boundary conditions and timeline
# ---------------------------------------------------------------------------


def test_phase1_starts_at_rest(result) -> None:
    assert abs(result.phase1.a[0]) < 1e-6
    assert abs(result.phase1.v[0]) < 1e-6


def test_phase1_reaches_the_door(result, cfg) -> None:
    assert result.phase1.s[-1] == pytest.approx(cfg.arc_length, abs=1e-3)


def test_phase1_released_at_contact(result) -> None:
    assert abs(result.phase1.a[-1]) < 1e-6


def test_phase2_starts_at_rest(result) -> None:
    assert abs(result.phase2.a[0]) < 1e-6
    assert abs(result.phase2.v[0]) < 1e-6


def test_phase2_returns_the_distance(result, cfg) -> None:
    assert result.phase2.s[-1] == pytest.approx(-cfg.return_translation, abs=1e-3)


def test_phase2_ends_at_rest(result) -> None:
    assert abs(result.phase2.v[-1]) < 1e-3
    assert abs(result.phase2.a[-1]) < 1e-6


def test_phase_durations_are_the_equal_split(cfg) -> None:
    assert cfg.phase1_duration == pytest.approx(1.5)
    assert cfg.phase2_duration == pytest.approx(1.5)
    assert cfg.phase1_duration + cfg.phase2_duration == pytest.approx(cfg.total_time)


def test_structural_durations_fill_the_phase(result, cfg) -> None:
    p1 = result.phase1
    total = p1.t_give + p1.t_plateau + p1.t_letgo + p1.t_coast
    assert total == pytest.approx(cfg.phase1_duration, abs=1e-6)


def test_ramps_are_literature_pinned(result, cfg) -> None:
    # the give and let-go ramps are fixed to the configured RFD-band values
    assert result.phase1.t_give == pytest.approx(cfg.t_give)
    assert result.phase1.t_letgo == pytest.approx(cfg.t_letgo)


# ---------------------------------------------------------------------------
# Production limits
# ---------------------------------------------------------------------------


def test_acceleration_within_ceiling(result, cfg) -> None:
    assert result.phase1.a_peak <= cfg.a_max_ceiling + 1e-6
    assert result.phase2.a_peak <= cfg.a_max_ceiling + 1e-6


def test_jerk_within_ceiling(result, cfg) -> None:
    assert result.phase1.jerk_peak <= cfg.jerk_ceiling + 1e-6
    assert result.phase2.jerk_peak <= cfg.jerk_ceiling + 1e-6


def test_feasible_flag_reflects_limits(result, cfg) -> None:
    within = (
        result.phase1.a_peak <= cfg.a_max_ceiling
        and result.phase2.a_peak <= cfg.a_max_ceiling
        and result.phase1.jerk_peak <= cfg.jerk_ceiling
        and result.phase2.jerk_peak <= cfg.jerk_ceiling
    )
    assert result.feasible == within


# ---------------------------------------------------------------------------
# No artefacts
# ---------------------------------------------------------------------------


def test_no_nan_or_inf(result) -> None:
    for ph in (result.phase1, result.phase2):
        for arr in (ph.s, ph.v, ph.a, ph.jerk):
            assert np.all(np.isfinite(arr))


def test_trajectory_is_continuous(result) -> None:
    """C2 by construction (smootherstep ramps) - no jumps in s, v, a."""
    for ph in (result.phase1, result.phase2):
        for arr in (ph.s, ph.v, ph.a):
            rng = float(np.ptp(arr))
            if rng > 1e-9:
                assert np.abs(np.diff(arr)).max() < 0.05 * rng


def test_phase1_acceleration_is_a_single_positive_lobe(result) -> None:
    """Phase 1 is a smooth trapezoid - acceleration never changes sign."""
    a = result.phase1.a
    significant = a[np.abs(a) > 0.05 * np.abs(a).max()]
    sign_changes = int(np.sum(np.diff(np.sign(significant)) != 0))
    assert sign_changes == 0


def test_phase1_velocity_monotonic(result) -> None:
    assert np.all(np.diff(result.phase1.v) > -1e-4)


def test_phase1_position_monotonic(result) -> None:
    assert np.all(np.diff(result.phase1.s) > -1e-6)


# ---------------------------------------------------------------------------
# Decoupled-singularity invariants
# ---------------------------------------------------------------------------


def test_closing_velocity_is_physical(result) -> None:
    """v_close must be a real, non-zero closing speed."""
    assert 1.0 < result.v_close < 5.0


def test_compression_matches_duration_and_velocity(result) -> None:
    s = result.singularity
    assert s.compression == pytest.approx(0.5 * s.v_close * s.tau_imp, rel=1e-9)


def test_compression_within_literature_range(result, cfg) -> None:
    d = result.singularity.compression
    assert cfg.body_compression_min - 1e-9 <= d <= cfg.body_compression_max + 1e-9


def test_singularity_force_is_severe_and_positive(result) -> None:
    assert result.singularity.force_peak > 0.0
    assert result.singularity.a_peak_g > 1.0


def test_impact_peak_monotonic_in_yield_stiffness(result, cfg) -> None:
    peaks = [
        impact_singularity(result.v_close, result.singularity.tau_imp, cfg, m).a_peak
        for m in YIELD_FACTORS
    ]
    assert peaks == sorted(peaks)


# ---------------------------------------------------------------------------
# Free parameters and constraints metadata
# ---------------------------------------------------------------------------


def test_free_parameters_are_constrained_not_eliminated(cfg) -> None:
    # every parameter is retained, each with a permissible range and a
    # stated source for that bound - literature does not remove parameters
    params = free_parameters(cfg)
    assert params
    for p in params:
        assert p.permissible_range
        assert p.bounded_by
        assert p.unit
        assert p.symbol


def test_constraints_have_sources(cfg) -> None:
    cons = constraints(cfg)
    assert cons
    for c in cons:
        assert c.source, f"constraint {c.name} has no source"
        assert c.kind in ("equality", "inequality")


def test_production_limits_cite_literature(cfg) -> None:
    inequality = [c for c in constraints(cfg) if c.kind == "inequality"]
    assert len(inequality) >= 3
    for c in inequality:
        assert "boundary condition" not in c.source


# ---------------------------------------------------------------------------
# Kinematics envelope - the two bracketing solutions
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def with_coast(cfg):
    return solve_choreography(cfg, release_standoff=2.0 * cfg.body_thickness)


def test_no_coast_solution_has_zero_coast(result) -> None:
    # the default solve is the no-coast envelope endpoint
    assert result.phase1.t_coast < 1e-2


def test_with_coast_solution_has_nonzero_coast(with_coast) -> None:
    assert with_coast.phase1.t_coast > 0.05


def test_envelope_brackets_closing_velocity(result, with_coast) -> None:
    # no-coast propels furthest -> highest v_close; with-coast releases
    # early -> lower v_close. The real motion lies between them.
    assert result.v_close > with_coast.v_close


def test_with_coast_coast_distance_matches_standoff(with_coast, cfg) -> None:
    # the body coasts the last 2x body thickness at constant v_close
    coast_distance = with_coast.v_close * with_coast.phase1.t_coast
    assert coast_distance == pytest.approx(2.0 * cfg.body_thickness, rel=0.1)


def test_with_coast_still_reaches_the_door(with_coast, cfg) -> None:
    assert with_coast.phase1.s[-1] == pytest.approx(cfg.arc_length, abs=1e-3)
