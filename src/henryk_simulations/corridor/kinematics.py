"""Analytical phase-by-phase kinematics.

Two models live in this module:

1. **Triangular peaks per phase** (`v_peak`, `a_peak`, `f_peak`): assumes a
   symmetric accel-decel within each phase so the body is at rest at both
   boundaries. Conservative; minimises required peak force.

2. **Continuous velocity across phases** (`v_start`, `v_end`, `a_avg`,
   `f_avg`, `impulse_net`, `ke_start`, `ke_end`, `work_done`): tracks the
   driven body's velocity as it carries through phase boundaries. Constant
   acceleration within each phase. Allows an impact event (sudden
   deceleration over a short stopping distance) to be modelled separately
   via `ImpactResult`.

Both models are computed for every phase. The reports use whichever is
more informative for the kinematic question being asked.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from henryk_simulations.corridor.config import Phase, ResistanceModel, Scenario

G = 9.80665  # m/s^2
MU_RESIST = 0.30  # static friction equivalent for an unsteady standing adult on tile
BRAKE_FORCE = 50.0  # N, modest active counter-effort in the 'small' resistance model
ARM_MASS_FRAC = 0.05  # mass of one arm, fraction of total body mass (Plagenhoef)
DEFAULT_IMPACT_STOPPING_DISTANCE = 0.02  # m, 2 cm: tissue + door flex + slight torso travel


@dataclass(frozen=True)
class ImpactResult:
    """Kinematics of a body decelerating from `v_impact` to rest over
    `stopping_distance`."""

    phase_name: str
    mass: float
    v_impact: float  # m/s at wall contact
    stopping_distance: float  # m
    ke_impact: float  # J = 0.5 m v^2
    momentum: float  # kg m/s = m v
    a_impact: float  # m/s^2 (constant-decel approximation)
    a_impact_g: float  # in g
    f_impact: float  # N (= m a_impact)
    t_stop: float  # s (= v / a_impact)


def compute_impact(
    *,
    phase_name: str,
    mass: float,
    v_impact: float,
    stopping_distance: float = DEFAULT_IMPACT_STOPPING_DISTANCE,
) -> ImpactResult:
    """Constant-deceleration impact over `stopping_distance`."""
    if v_impact <= 0:
        return ImpactResult(
            phase_name=phase_name,
            mass=mass,
            v_impact=0,
            stopping_distance=stopping_distance,
            ke_impact=0,
            momentum=0,
            a_impact=0,
            a_impact_g=0,
            f_impact=0,
            t_stop=0,
        )
    a = v_impact * v_impact / (2.0 * stopping_distance)
    return ImpactResult(
        phase_name=phase_name,
        mass=mass,
        v_impact=v_impact,
        stopping_distance=stopping_distance,
        ke_impact=0.5 * mass * v_impact * v_impact,
        momentum=mass * v_impact,
        a_impact=a,
        a_impact_g=a / G,
        f_impact=mass * a,
        t_stop=v_impact / a,
    )


@dataclass(frozen=True)
class PhaseResult:
    """Outcome of computing kinematic demands for one phase."""

    phase_name: str
    body: str
    kind: str
    mass: float  # kg
    duration: float  # s

    # Translation - triangular peaks (assumes accel-then-decel within phase)
    distance: float  # m
    v_peak: float  # m/s
    a_peak: float  # m/s^2
    a_peak_g: float
    f_peak: float  # N
    f_resist: float  # N (resistance contribution to f_peak)
    impulse: float  # N s, accel-only impulse (= m v_peak)
    kinetic_energy: float  # J at v_peak
    momentum_peak: float  # kg m/s at v_peak

    # Translation - continuous velocity model
    v_start: float  # m/s entering the phase
    v_end: float  # m/s at end of phase (before any impact)
    v_avg: float  # m/s mean velocity over the phase
    a_avg: float  # m/s^2 mean acceleration over the phase
    f_avg: float  # N mean applied force
    impulse_net: float  # N s = m (v_end - v_start)
    ke_start: float  # J
    ke_end: float  # J
    work_done: float  # J = ke_end - ke_start

    # Rotation
    angle: float  # rad
    omega_peak: float  # rad/s
    alpha_peak: float  # rad/s^2
    torque_peak: float  # N m
    angular_momentum_peak: float  # kg m^2/s
    rotational_ke: float  # J

    # Reach
    reach_distance: float
    reach_v_peak: float
    reach_a_peak: float
    reach_f_peak: float

    # Diagnostics
    resistance_model: str

    # Impact event (set only for the phase where the body hits a wall)
    impact: ImpactResult | None = None


def compute_phase_kinematics(
    phase: Phase,
    *,
    mass: float,
    yaw_inertia: float,
    resistance: ResistanceModel = "passive",
    arm_mass: float | None = None,
    v_start: float = 0.0,
    impact: ImpactResult | None = None,
) -> PhaseResult:
    """Compute kinematic demands for one phase.

    `v_start` is the body's velocity entering the phase (used by the
    continuous-velocity model). For the triangular-peak quantities the
    phase is treated as starting from rest within itself.
    """
    if arm_mass is None:
        arm_mass = ARM_MASS_FRAC * mass

    # Worst-case no-resistance: V is treated as deadweight, no friction or
    # brake opposing the motion. The previously-supported "small" variant
    # has been retired - it was strictly friendlier to the actor and not
    # informative for the plausibility question.
    f_resist = 0.0

    # Triangular-peak translation
    v_peak = a_peak = f_peak = impulse_triangular = ke = mom = 0.0
    if phase.kind == "translate" and phase.translation > 0:
        s = phase.translation
        t = phase.duration
        v_peak = 2.0 * s / t
        a_peak = 4.0 * s / (t * t)
        f_peak = mass * a_peak + f_resist
        impulse_triangular = mass * v_peak
        ke = 0.5 * mass * v_peak * v_peak
        mom = mass * v_peak

    # Continuous-velocity translation (constant accel within phase + impact
    # may zero the velocity early).
    v_end = v_avg = a_avg = f_avg = impulse_net = ke_start = ke_end = work = 0.0
    if phase.kind == "translate" and phase.translation > 0:
        s = phase.translation
        t = phase.duration
        v_avg_natural = s / t
        if impact is None:
            # Constant acceleration from v_start over the phase: distance =
            # v_start * t + 0.5 * a * t^2 -> a = 2 (s - v_start t) / t^2
            a_avg = 2.0 * (s - v_start * t) / (t * t)
            v_end = v_start + a_avg * t
        else:
            # Body hits a wall during the phase; treat the analytical phase
            # as ending at rest after the impact stop.
            v_end = 0.0
            a_avg = (v_end - v_start) / t
        v_avg = (v_start + v_end) / 2 if impact is None else v_avg_natural
        f_avg = mass * abs(a_avg) + f_resist
        impulse_net = mass * (v_end - v_start)
        ke_start = 0.5 * mass * v_start * v_start
        ke_end = 0.5 * mass * v_end * v_end
        work = ke_end - ke_start
    else:
        v_end = v_start

    # Rotation
    omega_peak = alpha_peak = torque_peak = ang_mom = rke = 0.0
    if phase.rotation > 0 and phase.kind in ("rotate", "translate"):
        theta = phase.rotation
        t = phase.duration
        omega_peak = 2.0 * theta / t
        alpha_peak = 4.0 * theta / (t * t)
        torque_peak = yaw_inertia * alpha_peak
        ang_mom = yaw_inertia * omega_peak
        rke = 0.5 * yaw_inertia * omega_peak * omega_peak

    # Reach
    reach_v = reach_a = reach_f = 0.0
    if phase.kind == "reach" and phase.reach > 0:
        s = phase.reach
        t = phase.duration
        reach_v = 2.0 * s / t
        reach_a = 4.0 * s / (t * t)
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
        impulse=impulse_triangular,
        kinetic_energy=ke,
        momentum_peak=mom,
        v_start=v_start,
        v_end=v_end,
        v_avg=v_avg,
        a_avg=a_avg,
        f_avg=f_avg,
        impulse_net=impulse_net,
        ke_start=ke_start,
        ke_end=ke_end,
        work_done=work,
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
        impact=impact,
    )


def compute_scenario(
    scenario: Scenario,
    *,
    resistance: ResistanceModel = "passive",
    impact_stopping_distance: float = DEFAULT_IMPACT_STOPPING_DISTANCE,
) -> list[PhaseResult]:
    """Compute kinematics for every phase.

    Tracks Victoria's velocity continuously across phases. The phase whose
    name is 'swap-throw' is treated as ending with V impacting the
    elevator wall: V's velocity at the start of the phase becomes the
    impact velocity and the phase's continuous-velocity model ends at rest.
    The impact result is attached to that phase.
    """
    bodies = scenario.bodies
    results: list[PhaseResult] = []
    v_current_m = 0.0
    v_current_h = 0.0
    for phase in scenario.phases:
        if phase.body == "M":
            mass = bodies.m_mass
            yaw_i = bodies.yaw_inertia_m
            v_start = v_current_m
        elif phase.body == "H":
            mass = bodies.h_mass
            yaw_i = bodies.yaw_inertia_h
            v_start = v_current_h
        else:
            mass = bodies.h_mass
            yaw_i = bodies.yaw_inertia_h
            v_start = v_current_h

        impact_result: ImpactResult | None = None
        if phase.name == "swap-throw":
            # V hits the elevator wall at the velocity she carried in.
            impact_result = compute_impact(
                phase_name=phase.name,
                mass=bodies.m_mass,
                v_impact=v_current_m,
                stopping_distance=impact_stopping_distance,
            )

        result = compute_phase_kinematics(
            phase,
            mass=mass,
            yaw_inertia=yaw_i,
            resistance=resistance,
            v_start=v_start,
            impact=impact_result,
        )
        results.append(result)

        # Update tracked velocities
        if phase.body == "M":
            v_current_m = result.v_end
        elif phase.body == "H":
            v_current_h = result.v_end

        # Secondary body motion within the same phase (e.g. V's 0.40 m
        # step-back during the swap-back while A is the primary actor).
        if phase.other_translation > 0 or phase.other_rotation > 0:
            if phase.body == "H":
                sec_body = "M"
                sec_mass = bodies.m_mass
                sec_yaw = bodies.yaw_inertia_m
                sec_v_start = v_current_m
            else:
                sec_body = "H"
                sec_mass = bodies.h_mass
                sec_yaw = bodies.yaw_inertia_h
                sec_v_start = v_current_h
            secondary_kind = "translate" if phase.other_translation > 0 else "rotate"
            sec_phase = Phase(
                name=f"{phase.name}/{sec_body}",
                duration=phase.duration,
                kind=secondary_kind,
                body=sec_body,
                translation=phase.other_translation,
                rotation=phase.other_rotation,
            )
            sec_result = compute_phase_kinematics(
                sec_phase,
                mass=sec_mass,
                yaw_inertia=sec_yaw,
                resistance=resistance,
                v_start=sec_v_start,
                impact=None,
            )
            results.append(sec_result)
            if sec_body == "M":
                v_current_m = sec_result.v_end
            else:
                v_current_h = sec_result.v_end

    return results


def actor_effort_for_translation(result: PhaseResult, actor_mass: float) -> dict[str, float]:
    """Forces the actor must apply through feet/contact to deliver `result`."""
    f_required = result.f_peak
    f_friction_cap = MU_RESIST * actor_mass * G
    return {
        "f_required_N": f_required,
        "f_friction_cap_N": f_friction_cap,
        "feasible": f_required <= f_friction_cap,
        "headroom_ratio": (f_friction_cap / f_required) if f_required > 0 else float("inf"),
    }


__all__ = [
    "ARM_MASS_FRAC",
    "BRAKE_FORCE",
    "DEFAULT_IMPACT_STOPPING_DISTANCE",
    "G",
    "MU_RESIST",
    "ImpactResult",
    "PhaseResult",
    "actor_effort_for_translation",
    "compute_impact",
    "compute_phase_kinematics",
    "compute_scenario",
]

_ = Literal
