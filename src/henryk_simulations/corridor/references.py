"""Biomechanical reference distributions for plausibility scoring.

Each reference is a scipy.stats frozen distribution paired with a name,
units, and citation. Distributions are normal with mean / SD drawn from
the cited sources; the SD reflects between-subject variation in the
referenced population (typically adult untrained or recreationally
active males unless noted).

Citations resolved in references/biomechanics-sources.md.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class Reference:
    """One biomechanical reference distribution."""

    name: str
    quantity: str  # what is measured
    distribution: stats.rv_frozen
    units: str
    citation: str
    population: str = "adult male, recreational"

    @property
    def mean(self) -> float:
        return float(self.distribution.mean())

    @property
    def sd(self) -> float:
        return float(self.distribution.std())

    def ci(self, level: float = 0.95) -> tuple[float, float]:
        """Two-sided confidence interval bounds."""
        a = (1.0 - level) / 2.0
        lo, hi = self.distribution.ppf([a, 1.0 - a])
        return float(lo), float(hi)

    def z(self, value: float) -> float:
        """Z-score of value against the reference."""
        return (value - self.mean) / self.sd

    def percentile(self, value: float) -> float:
        """Probability that a sampled subject does NOT reach the value."""
        return float(self.distribution.cdf(value))


@dataclass(frozen=True)
class ReferenceLibrary:
    """Collection of references keyed by short name."""

    refs: dict[str, Reference]

    def __getitem__(self, key: str) -> Reference:
        return self.refs[key]

    def keys(self) -> list[str]:
        return list(self.refs.keys())


def default_library() -> ReferenceLibrary:
    """Curated set of references used by the corridor analysis."""
    refs: dict[str, Reference] = {
        "push_force_single_arm": Reference(
            name="single-arm peak push, untrained male",
            quantity="peak push force, single dominant arm, standing",
            distribution=stats.norm(loc=400.0, scale=100.0),
            units="N",
            citation="Daams 1994; Mital & Kumar 1995",
        ),
        "push_force_two_arm": Reference(
            name="two-arm peak push, standing",
            quantity="peak push force, two arms, standing braced",
            distribution=stats.norm(loc=800.0, scale=200.0),
            units="N",
            citation="Daams 1994; Chaffin & Andersson 1991",
        ),
        "sprint_acceleration_recreational": Reference(
            name="sprint acceleration, recreational",
            quantity="peak forward acceleration, standing start",
            distribution=stats.norm(loc=3.0, scale=0.8),
            units="m/s^2",
            citation="Mero, Komi & Gregor 1992; di Prampero 2005",
        ),
        "sprint_acceleration_elite": Reference(
            name="sprint acceleration, elite sprinter",
            quantity="peak forward acceleration, standing start",
            distribution=stats.norm(loc=5.0, scale=0.5),
            units="m/s^2",
            citation="Mero, Komi & Gregor 1992",
            population="elite male sprinter",
        ),
        "throw_velocity_object_5kg": Reference(
            name="overhand throw velocity, 5 kg object",
            quantity="release velocity of a 5 kg object, overhand",
            distribution=stats.norm(loc=8.0, scale=2.5),
            units="m/s",
            citation="Cross 2004; Atwater 1979",
        ),
        "throw_kinetic_energy": Reference(
            name="overhand throw KE budget, 5 kg object",
            quantity="kinetic energy imparted to a 5 kg thrown object",
            distribution=stats.norm(loc=160.0, scale=80.0),
            units="J",
            citation="Cross 2004; van den Tillaar & Ettema 2004",
        ),
        "yaw_angular_velocity_pivot": Reference(
            name="standing pivot yaw angular velocity",
            quantity="peak yaw angular velocity during 180 deg standing turn",
            distribution=stats.norm(loc=3.5, scale=1.0),
            units="rad/s",
            citation="Hodgson, Lewis & Drury 2008",
        ),
        "whole_body_yaw_inertia": Reference(
            name="whole-body yaw moment of inertia",
            quantity="moment of inertia about vertical CoM axis, standing",
            distribution=stats.norm(loc=1.5, scale=0.4),
            units="kg*m^2",
            citation="Plagenhoef, Evans & Abdelnour 1983",
        ),
        "arm_swing_velocity": Reference(
            name="arm swing forward velocity",
            quantity="hand peak velocity during reach with extension",
            distribution=stats.norm(loc=2.5, scale=0.8),
            units="m/s",
            citation="Marteniuk, MacKenzie & Leavitt 1990",
        ),
    }
    return ReferenceLibrary(refs=refs)


def bootstrap_ci(
    distribution: stats.rv_frozen,
    n: int = 10_000,
    level: float = 0.95,
    rng: np.random.Generator | None = None,
) -> tuple[float, float]:
    """Empirical CI from sampling - useful for non-normal references later."""
    if rng is None:
        rng = np.random.default_rng(0)
    samples = distribution.rvs(size=n, random_state=rng)
    a = (1 - level) / 2 * 100
    return float(np.percentile(samples, a)), float(np.percentile(samples, 100 - a))


__all__ = [
    "Reference",
    "ReferenceLibrary",
    "bootstrap_ci",
    "default_library",
]
