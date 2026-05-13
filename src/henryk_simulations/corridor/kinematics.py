"""Analytical phase-by-phase kinematics.

Uses the simplest defensible kinematic model: constant acceleration over each
phase so that the peak acceleration and peak velocity are bounded above by
twice the average values for a symmetric accel-decel triangle profile.

For a triangular velocity profile (accelerate for t/2, decelerate for t/2)
covering distance s in time t:
    v_peak = 2 * s / t
    a_peak = 4 * s / t^2
    impulse = m * v_peak (delivered by the actor; returned at deceleration)
    work_done = (1/2) * m * v_peak^2 (kinetic energy at midpoint)

For a 'small resistance' model an additional constant opposing force is added:
    F_resist = mu_static * m * g + active_brake
where mu_static is a friction-equivalent coefficient (~0.3 for shoes on tile)
and active_brake is a modest counter-effort (~50 N). The actor must overcome
this friction in addition to providing the inertial force.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from henryk_simulations.corridor.config import Phase, ResistanceModel, Scenario

G = 9.80665  # m/s^2
MU_RESIST = 0.30  # static friction equivalent for an unsteady standing adult on tile
BRAKE_FORCE = 50.0  # N, modest active counter-effort in the 'small' resistance model
ARM_MASS_FRAC = 0.05  # mass of one arm, fraction of total body mass (Plagenhoef)


@dataclass(frozen=True)
class PhaseResult:
    """Outcome of computing kinematic demands for one phase."""

    phase_name: str
    body: str
    kind: str
    mass: float  # kg of the body being driven (for translate/rotate)
    duration: float  # s
    # Translation kinematics (zero if not applicable)
    distance: float  # m
    v_peak: float  # m/s
    a_peak: float  # m/s^2
    a_peak_g: float  # peak accel expressed in g
    f_peak: float  # N, peak applied force including resistance
    f_resist: float  # N, resistance contribution
    impulse: float  # N*s
    kinetic_energy: float  # J
    momentum_peak: float  # kg*m/s
    # Rotation kinematics
    angle: float  # rad
    omega_peak: float  # rad/s
    alpha_peak: float  # rad/s^2
    torque_peak: float  # N*m
    angular_momentum_peak: float  # kg*m^2/s
    rotational_ke: float  # J
    # Reach kinematics
    reach_distance: float  # m
    reach_v_peak: float  # m/s
    reach_a_peak: float  # m/s^2
    reach_f_peak: float  # N (force at hand to accelerate arm + neutral payload)
    # Diagnostics
    resistance_model: str


def compute_phase_kinematics(
    phase: Phase,
    *,
    mass: float,
    yaw_inertia: float,
    resistance: ResistanceModel = "passive",
    arm_mass: float | None = None,
) -> PhaseResult:
    """Compute peak demands for one phase.

    Parameters
    ----------
    phase           Phase definition
    mass            mass of the body being driven (kg)
    yaw_inertia     moment of inertia about the yaw axis (kg m^2)
    resistance      "passive" deadweight or "small" friction + brake
    arm_mass        kg; defaults to ARM_MASS_FRAC * mass for reach phases
    """
    if arm_mass is None:
        arm_mass = ARM_MASS_FRAC * mass

    f_resist = 0.0
    if resistance == "small" and phase.kind == "translate":
        f_resist = MU_RESIST * mass * G + BRAKE_FORCE

    # Translation block
    v_peak = a_peak = f_peak = impulse = ke = mom = 0.0
    if phase.kind == "translate" and phase.translation > 0:
        s = phase.translation
        t = phase.duration
        v_peak = 2.0 * s / t
        a_peak = 4.0 * s / (t * t)
        f_peak = mass * a_peak + f_resist
        impulse = mass * v_peak
        ke = 0.5 * mass * v_peak * v_peak
        mom = mass * v_peak

    # Rotation block - either a dedicated rotate phase or rotation concurrent
    # with translation in the same phase.
    omega_peak = alpha_peak = torque_peak = ang_mom = rke = 0.0
    if phase.rotation > 0 and phase.kind in ("rotate", "translate"):
        theta = phase.rotation
        t = phase.duration
        omega_peak = 2.0 * theta / t
        alpha_peak = 4.0 * theta / (t * t)
        torque_peak = yaw_inertia * alpha_peak
        ang_mom = yaw_inertia * omega_peak
        rke = 0.5 * yaw_inertia * omega_peak * omega_peak

    # Reach block (arm extension)
    reach_v = reach_a = reach_f = 0.0
    if phase.kind == "reach" and phase.reach > 0:
        s = phase.reach
        t = phase.duration
        reach_v = 2.0 * s / t
        reach_a = 4.0 * s / (t * t)
        # Treat as two-arm extension carrying its own inertia
        reach_f = 2.0 * arm_mass * reach_a

    return PhaseResult(
        phase_name=phase.name,
        body=phase.body,
        kind=phase.kind,
        mass=mass,
        duration=phase.duration,
        distance=phase.translation,
        v_peak=v_peak,
        a_peak=a_peak,
        a_peak_g=a_peak / G if a_peak else 0.0,
        f_peak=f_peak,
        f_resist=f_resist,
        impulse=impulse,
        kinetic_energy=ke,
        momentum_peak=mom,
        angle=phase.rotation,
        omega_peak=omega_peak,
        alpha_peak=alpha_peak,
        torque_peak=torque_peak,
        angular_momentum_peak=ang_mom,
        rotational_ke=rke,
        reach_distance=phase.reach,
        reach_v_peak=reach_v,
        reach_a_peak=reach_a,
        reach_f_peak=reach_f,
        resistance_model=resistance,
    )


def compute_scenario(
    scenario: Scenario,
    *,
    resistance: ResistanceModel = "passive",
) -> list[PhaseResult]:
    """Compute kinematics for every phase in the scenario.

    For phase.body == "both" the result is computed for the body whose mass
    drives the worst-case demand (the lighter body needs less force but the
    heavier body sets the actor effort floor for active throws).
    """
    bodies = scenario.bodies
    results: list[PhaseResult] = []
    for phase in scenario.phases:
        if phase.body == "M":
            mass = bodies.m_mass
            yaw_i = bodies.yaw_inertia_m
        elif phase.body == "H":
            mass = bodies.h_mass
            yaw_i = bodies.yaw_inertia_h
        else:  # both - use heavier body for the conservative force demand
            mass = bodies.h_mass
            yaw_i = bodies.yaw_inertia_h
        results.append(
            compute_phase_kinematics(
                phase,
                mass=mass,
                yaw_inertia=yaw_i,
                resistance=resistance,
            ),
        )
    return results


def actor_effort_for_translation(result: PhaseResult, actor_mass: float) -> dict[str, float]:
    """Forces the actor must apply through their feet/contact to deliver `result`.

    Newton's 3rd law: the force on the driven body equals the reaction on the
    actor. Actor's centre-of-mass acceleration during the push, if the actor
    is not also translating, is bounded by ground-reaction friction:
        F_ground <= mu_dyn * actor_mass * g
    """
    f_required = result.f_peak  # what the actor must exert on the body
    f_friction_cap = MU_RESIST * actor_mass * G  # ground reaction available
    return {
        "f_required_N": f_required,
        "f_friction_cap_N": f_friction_cap,
        "feasible": f_required <= f_friction_cap,
        "headroom_ratio": (f_friction_cap / f_required) if f_required > 0 else float("inf"),
    }


__all__ = [
    "ARM_MASS_FRAC",
    "BRAKE_FORCE",
    "G",
    "MU_RESIST",
    "PhaseResult",
    "actor_effort_for_translation",
    "compute_phase_kinematics",
    "compute_scenario",
]

# Linter pacification - Literal import is part of public type surface above.
_ = Literal
