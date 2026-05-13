"""Plausibility scoring: compare phase demand vs reference distribution."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from henryk_simulations.corridor.kinematics import PhaseResult
from henryk_simulations.corridor.references import Reference


class Verdict(str, Enum):
    PLAUSIBLE = "plausible"
    STRAINED = "strained"
    IMPLAUSIBLE = "implausible"
    EXTREME = "extreme"


def verdict_from_z(z: float) -> Verdict:
    """Verdict bands by z-score above the reference mean."""
    if z <= 1.0:
        return Verdict.PLAUSIBLE
    if z <= 2.0:
        return Verdict.STRAINED
    if z <= 3.0:
        return Verdict.IMPLAUSIBLE
    return Verdict.EXTREME


@dataclass(frozen=True)
class PlausibilityScore:
    """Outcome of comparing one phase demand to one reference."""

    phase_name: str
    quantity_label: str
    required_value: float
    units: str
    reference_name: str
    reference_mean: float
    reference_sd: float
    reference_ci_lo: float
    reference_ci_hi: float
    z: float
    percentile: float  # P(reference subject below required value)
    multiple_of_mean: float
    verdict: Verdict
    citation: str


def score_phase(
    *,
    required_value: float,
    quantity_label: str,
    units: str,
    phase_name: str,
    reference: Reference,
    ci_level: float = 0.95,
) -> PlausibilityScore:
    """Score one (phase, quantity) pair against one reference."""
    ci_lo, ci_hi = reference.ci(ci_level)
    z = reference.z(required_value)
    pct = reference.percentile(required_value)
    return PlausibilityScore(
        phase_name=phase_name,
        quantity_label=quantity_label,
        required_value=required_value,
        units=units,
        reference_name=reference.name,
        reference_mean=reference.mean,
        reference_sd=reference.sd,
        reference_ci_lo=ci_lo,
        reference_ci_hi=ci_hi,
        z=z,
        percentile=pct,
        multiple_of_mean=required_value / reference.mean if reference.mean else float("inf"),
        verdict=verdict_from_z(z),
        citation=reference.citation,
    )


def score_translation_phase(
    result: PhaseResult,
    *,
    accel_ref: Reference,
    force_ref: Reference,
    energy_ref: Reference | None = None,
) -> list[PlausibilityScore]:
    """Score a translation phase against accel, force, and (optionally) energy refs."""
    scores = [
        score_phase(
            required_value=result.a_peak,
            quantity_label="peak acceleration",
            units="m/s^2",
            phase_name=result.phase_name,
            reference=accel_ref,
        ),
        score_phase(
            required_value=result.f_peak,
            quantity_label="peak force",
            units="N",
            phase_name=result.phase_name,
            reference=force_ref,
        ),
    ]
    if energy_ref is not None:
        scores.append(
            score_phase(
                required_value=result.kinetic_energy,
                quantity_label="kinetic energy",
                units="J",
                phase_name=result.phase_name,
                reference=energy_ref,
            ),
        )
    return scores


def score_rotation_phase(
    result: PhaseResult,
    *,
    omega_ref: Reference,
) -> list[PlausibilityScore]:
    """Score a rotation phase against angular velocity reference."""
    return [
        score_phase(
            required_value=result.omega_peak,
            quantity_label="peak yaw angular velocity",
            units="rad/s",
            phase_name=result.phase_name,
            reference=omega_ref,
        ),
    ]


def score_reach_phase(
    result: PhaseResult,
    *,
    arm_ref: Reference,
) -> list[PlausibilityScore]:
    """Score a reach phase against hand velocity reference."""
    return [
        score_phase(
            required_value=result.reach_v_peak,
            quantity_label="peak hand velocity",
            units="m/s",
            phase_name=result.phase_name,
            reference=arm_ref,
        ),
    ]


__all__ = [
    "PlausibilityScore",
    "Verdict",
    "score_phase",
    "score_reach_phase",
    "score_rotation_phase",
    "score_translation_phase",
    "verdict_from_z",
]
