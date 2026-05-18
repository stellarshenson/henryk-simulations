"""Guards for the back-impact dynamics model.

These tests verify the lumped-parameter posterior-thorax model **obeys its
constraints** (mass balance, contact non-negativity, bounded impulse) and
**produces no artefacts** (no NaN, no force without penetration, the yield
plateau caps the force).
"""

from __future__ import annotations

import numpy as np
import pytest
from scipy.integrate import trapezoid

from henryk_simulations.corridor import (
    ImpactConfig,
    assess_fracture,
    body_segments,
    contact_area,
    effective_impact_mass,
    fracture_thresholds,
    ribs_engaged,
    solve_impact,
    solve_impact_envelope,
)
from henryk_simulations.corridor.impact import POSTERIOR_PATCHES


@pytest.fixture(scope="module")
def cfg() -> ImpactConfig:
    return ImpactConfig()


@pytest.fixture(scope="module")
def result(cfg):
    return solve_impact(cfg, 2.738)


# ---------------------------------------------------------------------------
# Body segments and effective mass
# ---------------------------------------------------------------------------


def test_segment_masses_sum_to_body_mass(cfg) -> None:
    total = sum(s.mass for s in body_segments(cfg))
    assert total == pytest.approx(cfg.body_mass, rel=1e-9)


def test_segments_partition_into_back_and_limb(cfg) -> None:
    for s in body_segments(cfg):
        assert s.group in ("back", "limb")


def test_chain_masses_sum_to_body_mass(cfg) -> None:
    chain = cfg.m_skin + cfg.m_scapula + cfg.m_ribcage + cfg.m_organ + cfg.m_spine
    assert chain == pytest.approx(cfg.body_mass, rel=1e-9)


def test_effective_mass_back_below_full_body(cfg) -> None:
    em = effective_impact_mass(cfg)
    assert 0.0 < em.m_back < cfg.body_mass


def test_effective_mass_envelope_ordering(cfg) -> None:
    em = effective_impact_mass(cfg)
    assert em.m_eff_low < em.m_eff_high
    assert em.m_eff_low == pytest.approx(em.m_back)
    assert em.m_eff_high == pytest.approx(cfg.body_mass)


# ---------------------------------------------------------------------------
# Contact patches and area build-up
# ---------------------------------------------------------------------------


def test_contact_area_starts_at_initial(cfg) -> None:
    assert contact_area(np.array([0.0]), cfg)[0] == pytest.approx(cfg.area_initial)


def test_contact_area_monotone_nondecreasing(cfg) -> None:
    a = contact_area(np.linspace(0.0, cfg.t_max, 500), cfg)
    assert np.all(np.diff(a) >= -1e-12)


def test_contact_area_bounded_by_final(cfg) -> None:
    a = contact_area(np.linspace(0.0, 10.0, 500), cfg)
    assert np.all(a <= cfg.area_final + 1e-12)


def test_ribs_engaged_in_range(cfg) -> None:
    for area in (0.0, cfg.area_initial, cfg.area_final, 2 * cfg.area_final):
        assert 1.0 <= ribs_engaged(area, cfg) <= cfg.n_ribs_span


def test_posterior_patches_ordered() -> None:
    orders = [p.order for p in POSTERIOR_PATCHES]
    assert orders == sorted(orders)
    assert orders[0] == 1


# ---------------------------------------------------------------------------
# Impact ODE - no artefacts
# ---------------------------------------------------------------------------


def test_no_nan_or_inf(result) -> None:
    for arr in (
        result.f_contact,
        result.f_contact_capped,
        result.f_rib,
        result.f_spine,
        result.penetration,
        result.rib_compression,
        result.area,
        result.pressure,
    ):
        assert np.all(np.isfinite(arr))


def test_contact_force_nonnegative(result) -> None:
    assert np.all(result.f_contact >= 0.0)
    assert np.all(result.f_contact_capped >= 0.0)


def test_no_force_without_penetration(result) -> None:
    no_contact = result.penetration <= 0.0
    assert np.all(result.f_contact[no_contact] == 0.0)


def test_penetration_nonnegative(result) -> None:
    assert np.all(result.penetration >= 0.0)
    assert np.all(result.rib_compression >= 0.0)


# ---------------------------------------------------------------------------
# Impact ODE - physics and the yield plateau
# ---------------------------------------------------------------------------


def test_peak_force_is_physical(result) -> None:
    assert 1.0e3 < result.peak_force < 30.0e3


def test_capped_force_respects_yield(cfg, result) -> None:
    assert np.all(result.f_contact_capped <= cfg.yield_force + 1e-6)


def test_low_yield_caps_the_force(cfg) -> None:
    capped = solve_impact(cfg, 2.738, yield_force=2000.0)
    assert capped.f_contact_capped.max() <= 2000.0 + 1e-6


def test_contact_impulse_is_bounded(cfg, result) -> None:
    # the contact impulse cannot exceed a full elastic rebound of the body
    impulse = trapezoid(result.f_contact_capped, result.t)
    assert impulse <= 2.0 * cfg.body_mass * result.v_close + 1.0


def test_faster_impact_gives_higher_force(cfg) -> None:
    slow = solve_impact(cfg, 2.0)
    fast = solve_impact(cfg, 3.0)
    assert fast.peak_force > slow.peak_force


def test_kinetic_energy_matches_inflow(cfg, result) -> None:
    assert result.kinetic_energy == pytest.approx(0.5 * cfg.body_mass * result.v_close**2)


def test_per_rib_force_below_total(result) -> None:
    assert result.per_rib_force < result.peak_force
    assert result.ribs_engaged >= 1.0


# ---------------------------------------------------------------------------
# Kinematics envelope coupling
# ---------------------------------------------------------------------------


def test_envelope_returns_two_solutions(cfg) -> None:
    fast, slow = solve_impact_envelope(cfg)
    assert fast.v_close > slow.v_close


def test_envelope_brackets_the_force(cfg) -> None:
    fast, slow = solve_impact_envelope(cfg)
    assert fast.peak_force > slow.peak_force


# ---------------------------------------------------------------------------
# Fracture thresholds and verdict
# ---------------------------------------------------------------------------


def test_thresholds_have_positive_value_and_source() -> None:
    thresholds = fracture_thresholds()
    assert thresholds
    for t in thresholds:
        assert t.value > 0.0
        assert t.source
        assert t.unit


def test_assess_returns_a_verdict_per_check(result) -> None:
    verdicts = assess_fracture(result)
    assert len(verdicts) >= 5
    for v in verdicts:
        assert v.verdict in ("fracture", "borderline", "no fracture")
        assert v.source


def test_per_rib_verdict_is_no_fracture(result) -> None:
    # the distributed load over the engaged ribs stays below the rib-bending
    # fracture force - the envelope's load does not fracture individual ribs
    per_rib = [v for v in assess_fracture(result) if "per-rib" in v.quantity]
    assert per_rib
    for v in per_rib:
        assert v.verdict == "no fracture"


def test_verdict_escalates_with_velocity(cfg) -> None:
    # a far more violent impact must not score better than the envelope one
    envelope = solve_impact(cfg, 2.738)
    violent = solve_impact(cfg, 8.0)
    rank = {"no fracture": 0, "borderline": 1, "fracture": 2}
    env_force = next(v for v in assess_fracture(envelope) if v.quantity == "peak contact force")
    vio_force = next(v for v in assess_fracture(violent) if v.quantity == "peak contact force")
    assert rank[vio_force.verdict] >= rank[env_force.verdict]


def test_config_carries_subject_demographics(cfg) -> None:
    # sex and age are configuration parameters; the corridor subject is a
    # young-adult woman, so the default sex is "F" and the age unset
    assert cfg.subject_gender in ("F", "M")
    assert cfg.subject_gender == "F"
    assert cfg.subject_age is None  # None - assume a standard adult
    victoria = ImpactConfig(subject_gender="F", subject_age=28.0)
    assert victoria.subject_age == 28.0
