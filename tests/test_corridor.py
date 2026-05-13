"""Unit tests for corridor module: config, kinematics, references, plausibility."""

from __future__ import annotations

import math

import pytest

from henryk_simulations.corridor import (
    PhaseResult,
    PlausibilityScore,
    Verdict,
    compute_phase_kinematics,
    compute_scenario,
    default_library,
    default_scenario,
    score_phase,
)
from henryk_simulations.corridor.config import Geometry, Phase, Scenario
from henryk_simulations.corridor.kinematics import G, actor_effort_for_translation


# ---------------------------------------------------------------------------
# Config invariants
# ---------------------------------------------------------------------------


def test_default_scenario_durations_sum_to_total_time() -> None:
    sc = default_scenario()
    seq = sum(p.duration for p in sc.phases if p.overlaps_with is None)
    assert math.isclose(seq, sc.total_time, abs_tol=1e-9)


def test_default_scenario_has_three_phases() -> None:
    sc = default_scenario()
    assert len(sc.phases) == 3
    assert [p.name for p in sc.phases] == ["pull-out", "throw", "reverse"]


def test_phase_starts_are_monotonic_among_sequential() -> None:
    sc = default_scenario()
    seq_starts = [
        s
        for s, p in zip(sc.phase_starts, sc.phases)
        if p.overlaps_with is None
    ]
    assert seq_starts == sorted(seq_starts)


def test_scenario_rejects_mismatched_total_time() -> None:
    with pytest.raises(ValueError):
        Scenario(
            total_time=1.0,
            geometry=Geometry(),
            bodies=default_scenario().bodies,
            phases=(Phase("foo", 0.5, "translate", "M", translation=0.1),),
        )


def test_overlapping_phase_starts_at_host_tail() -> None:
    """Build a manual scenario with an overlapping phase to test the invariant."""
    sc = Scenario(
        total_time=1.0,
        geometry=Geometry(),
        bodies=default_scenario().bodies,
        phases=(
            Phase("a", 0.6, "translate", "M", translation=0.1),
            Phase("b", 0.3, "reach", "H", reach=0.2, overlaps_with=0),
            Phase("c", 0.4, "translate", "M", translation=0.1),
        ),
    )
    starts = sc.phase_starts
    expected = starts[0] + sc.phases[0].duration - sc.phases[1].duration
    assert math.isclose(starts[1], expected, abs_tol=1e-9)


# ---------------------------------------------------------------------------
# Kinematics
# ---------------------------------------------------------------------------


def test_constant_accel_formulas_for_throw_phase() -> None:
    """Triangular profile covering 2.0 m in 1.0 s (the 3-phase default throw):
    v_peak = 2*s/t = 4.0 m/s, a_peak = 4*s/t^2 = 8.0 m/s^2 (0.82g)."""
    phase = Phase("throw", 1.00, "translate", "M", translation=2.0)
    r = compute_phase_kinematics(phase, mass=70.0, yaw_inertia=1.4, resistance="passive")
    assert math.isclose(r.v_peak, 2 * 2.0 / 1.0, rel_tol=1e-9)
    assert math.isclose(r.a_peak, 4 * 2.0 / (1.0**2), rel_tol=1e-9)
    assert math.isclose(r.f_peak, 70.0 * r.a_peak, rel_tol=1e-9)
    assert r.kinetic_energy == pytest.approx(0.5 * 70.0 * r.v_peak**2)


def test_resistance_adds_friction_force_to_translate() -> None:
    phase = Phase("throw", 0.70, "translate", "M", translation=2.0)
    passive = compute_phase_kinematics(phase, mass=70.0, yaw_inertia=1.4, resistance="passive")
    small = compute_phase_kinematics(phase, mass=70.0, yaw_inertia=1.4, resistance="small")
    assert small.f_peak > passive.f_peak
    assert small.f_resist > 0


def test_rotation_phase_torque_matches_inertia_times_alpha() -> None:
    phase = Phase("reverse", 1.40, "rotate", "H", rotation=math.pi)
    r = compute_phase_kinematics(phase, mass=90.0, yaw_inertia=1.8, resistance="passive")
    assert math.isclose(r.alpha_peak, 4 * math.pi / (1.4**2), rel_tol=1e-9)
    assert math.isclose(r.torque_peak, 1.8 * r.alpha_peak, rel_tol=1e-9)
    assert math.isclose(r.omega_peak, 2 * math.pi / 1.4, rel_tol=1e-9)


def test_reach_phase_uses_arm_mass_default() -> None:
    phase = Phase("manual-reach", 0.40, "reach", "H", reach=0.70)
    r = compute_phase_kinematics(phase, mass=90.0, yaw_inertia=1.8)
    # Default arm mass = 0.05 * 90 = 4.5 kg per arm
    expected_a = 4 * 0.70 / (0.40**2)
    assert math.isclose(r.reach_a_peak, expected_a, rel_tol=1e-9)
    assert math.isclose(r.reach_f_peak, 2 * 4.5 * expected_a, rel_tol=1e-9)


def test_compute_scenario_returns_one_result_per_phase() -> None:
    sc = default_scenario()
    res = compute_scenario(sc)
    assert len(res) == len(sc.phases)
    assert all(isinstance(r, PhaseResult) for r in res)


def test_actor_effort_friction_cap() -> None:
    phase = Phase("throw", 1.00, "translate", "M", translation=2.0)
    r = compute_phase_kinematics(phase, mass=70.0, yaw_inertia=1.4)
    eff = actor_effort_for_translation(r, actor_mass=90.0)
    cap = 0.30 * 90.0 * G  # MU_RESIST * actor_mass * g
    assert math.isclose(eff["f_friction_cap_N"], cap, rel_tol=1e-9)
    assert eff["feasible"] is False  # 70 * 8 = 560 N required vs ~265 N cap


# ---------------------------------------------------------------------------
# References
# ---------------------------------------------------------------------------


def test_default_library_has_expected_keys() -> None:
    lib = default_library()
    for key in [
        "push_force_single_arm",
        "push_force_two_arm",
        "sprint_acceleration_recreational",
        "sprint_acceleration_elite",
        "throw_velocity_object_5kg",
        "throw_kinetic_energy",
        "yaw_angular_velocity_pivot",
        "whole_body_yaw_inertia",
        "arm_swing_velocity",
    ]:
        assert key in lib.keys()


def test_reference_z_score_zero_at_mean() -> None:
    lib = default_library()
    ref = lib["push_force_single_arm"]
    assert ref.z(ref.mean) == pytest.approx(0.0)


def test_reference_ci_brackets_mean() -> None:
    lib = default_library()
    ref = lib["push_force_two_arm"]
    lo, hi = ref.ci(0.95)
    assert lo < ref.mean < hi
    # 95% CI for normal is mean +/- 1.96 sigma
    assert math.isclose(hi - ref.mean, 1.959963984540054 * ref.sd, rel_tol=1e-3)


# ---------------------------------------------------------------------------
# Plausibility
# ---------------------------------------------------------------------------


def test_score_phase_returns_plausibility_score_with_correct_verdict() -> None:
    lib = default_library()
    ref = lib["push_force_two_arm"]
    # Value at mean -> plausible
    s = score_phase(
        required_value=ref.mean,
        quantity_label="peak force",
        units="N",
        phase_name="test",
        reference=ref,
    )
    assert isinstance(s, PlausibilityScore)
    assert s.verdict == Verdict.PLAUSIBLE
    # Value at mean + 4 sigma -> extreme
    s2 = score_phase(
        required_value=ref.mean + 4 * ref.sd,
        quantity_label="peak force",
        units="N",
        phase_name="test",
        reference=ref,
    )
    assert s2.verdict == Verdict.EXTREME


@pytest.mark.parametrize(
    ("z_target", "expected"),
    [
        (0.0, Verdict.PLAUSIBLE),
        (1.5, Verdict.STRAINED),
        (2.5, Verdict.IMPLAUSIBLE),
        (4.0, Verdict.EXTREME),
    ],
)
def test_verdict_bands(z_target: float, expected: Verdict) -> None:
    lib = default_library()
    ref = lib["sprint_acceleration_recreational"]
    value = ref.mean + z_target * ref.sd
    s = score_phase(
        required_value=value,
        quantity_label="peak acceleration",
        units="m/s^2",
        phase_name="test",
        reference=ref,
    )
    assert s.verdict == expected
