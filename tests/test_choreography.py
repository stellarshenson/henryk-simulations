"""Guards for the decoupled-singularity choreography model.

These tests verify the simulation **obeys its constraints** (boundary
conditions, biomechanical production limits) and **produces no artefacts**
(discontinuities, spurious oscillation, non-physical values). They are the
guards that catch a regression where the optimiser drifts into an exclusion
zone or the spline develops the infinite-jerk corners the smooth model was
built to eliminate.
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
    """Solve once - the QP solve is the expensive step."""
    return solve_choreography()


# ---------------------------------------------------------------------------
# Boundary conditions - the scenario equality constraints
# ---------------------------------------------------------------------------


def test_phase1_starts_at_rest(result) -> None:
    assert abs(result.phase1.a[0]) < 1e-6
    assert abs(result.phase1.v[0]) < 1e-6


def test_phase1_reaches_the_door(result, cfg) -> None:
    assert result.phase1.s[-1] == pytest.approx(cfg.arc_length, abs=1e-3)


def test_phase1_released_at_contact(result) -> None:
    # acceleration is zero at contact - the body coasts into the door
    assert abs(result.phase1.a[-1]) < 1e-6


def test_phase2_starts_at_rest(result) -> None:
    assert abs(result.phase2.a[0]) < 1e-6
    assert abs(result.phase2.v[0]) < 1e-6


def test_phase2_returns_the_distance(result, cfg) -> None:
    assert result.phase2.s[-1] == pytest.approx(-cfg.return_translation, abs=1e-3)


def test_phase2_ends_at_rest(result) -> None:
    assert abs(result.phase2.v[-1]) < 1e-4
    assert abs(result.phase2.a[-1]) < 1e-6


def test_phase_durations_sum_to_total(cfg) -> None:
    assert cfg.phase1_duration + cfg.phase2_duration == pytest.approx(cfg.total_time)


# ---------------------------------------------------------------------------
# Production limits - the exclusion zones, banned from the manifold
# ---------------------------------------------------------------------------


def test_acceleration_within_ceiling(result, cfg) -> None:
    assert result.phase1.a_peak <= cfg.a_max_ceiling + 1e-6
    assert result.phase2.a_peak <= cfg.a_max_ceiling + 1e-6


def test_jerk_within_ceiling(result, cfg) -> None:
    assert result.phase1.jerk_peak <= cfg.jerk_ceiling + 1e-6
    assert result.phase2.jerk_peak <= cfg.jerk_ceiling + 1e-6


def test_acceleration_limit_actively_enforced() -> None:
    """A ceiling below the natural jerk-minimal peak must force the
    optimiser down to it - proof the exclusion zone is genuinely banned,
    not merely checked after the fact."""
    tight = ChoreographyConfig(a_max_ceiling=2.3)  # natural peak is ~2.47
    res = solve_choreography(tight)
    assert res.phase1.a_peak <= 2.3 + 1e-2
    assert res.bounds_active


# ---------------------------------------------------------------------------
# No artefacts - smoothness, no spurious oscillation, physical values
# ---------------------------------------------------------------------------


def test_no_nan_or_inf(result) -> None:
    for ph in (result.phase1, result.phase2):
        for arr in (ph.s, ph.v, ph.a, ph.jerk):
            assert np.all(np.isfinite(arr))


def test_trajectory_is_continuous(result) -> None:
    """C2 by construction - verify no jumps: the largest step between
    adjacent samples stays far below the signal range."""
    for ph in (result.phase1, result.phase2):
        for arr in (ph.s, ph.v, ph.a):
            rng = float(np.ptp(arr))
            if rng > 1e-9:
                assert np.abs(np.diff(arr)).max() < 0.05 * rng


def test_phase1_acceleration_has_no_spurious_lobes(result) -> None:
    """Phase 1 accelerates then eases to zero - the acceleration is a
    single positive lobe. Spurious oscillation would flip the sign of the
    significant part more than once."""
    a = result.phase1.a
    significant = a[np.abs(a) > 0.05 * np.abs(a).max()]
    sign_changes = int(np.sum(np.diff(np.sign(significant)) != 0))
    assert sign_changes <= 1


def test_phase1_velocity_monotonic(result) -> None:
    # phase 1 accelerates from rest to v_close - velocity never decreases
    assert np.all(np.diff(result.phase1.v) > -1e-4)


def test_phase1_position_monotonic(result) -> None:
    assert np.all(np.diff(result.phase1.s) > -1e-6)


# ---------------------------------------------------------------------------
# Decoupled-singularity invariants
# ---------------------------------------------------------------------------


def test_closing_velocity_is_physical(result) -> None:
    """v_close must be a real, non-zero closing speed - the old global-spline
    model collapsed it to zero and starved the impact."""
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
    """A stiffer yield model must give a higher peak deceleration."""
    peaks = [
        impact_singularity(result.v_close, result.singularity.tau_imp, cfg, m).a_peak
        for m in YIELD_FACTORS
    ]
    assert peaks == sorted(peaks)


# ---------------------------------------------------------------------------
# Free parameters and constraints metadata
# ---------------------------------------------------------------------------


def test_free_parameters_have_valid_bounds(cfg) -> None:
    params = free_parameters(cfg)
    assert params
    for p in params:
        assert p.lower <= p.upper
        assert p.count > 0
        assert p.unit


def test_constraints_have_sources(cfg) -> None:
    cons = constraints(cfg)
    assert cons
    for c in cons:
        assert c.source, f"constraint {c.name} has no source"
        assert c.kind in ("equality", "inequality")


def test_production_limits_cite_literature(cfg) -> None:
    """Every inequality constraint - the production limits - must cite a
    literature source, not the generic scenario boundary-condition tag."""
    inequality = [c for c in constraints(cfg) if c.kind == "inequality"]
    assert len(inequality) >= 3
    for c in inequality:
        assert "boundary condition" not in c.source
