"""Decoupled-singularity smooth-choreography kinematics - structural model.

The corridor incident's kinematic model. The choreography is a two-phase
smooth trajectory - a phase-1 approach, a decoupled impact singularity, and
a phase-2 return - with the tangential acceleration parametrised by its
**structural durations** rather than by spline knots.

Phase 1 is a smooth trapezoid: a start ramp (the "give", ``a`` rising
``0 -> a_max``), a plateau, a release ramp (the "let-go", ``a`` falling
``a_max -> 0``), and a coast (``a = 0``). The give and let-go ramp times are
**literature-pinned** from the rate-of-force-development band; the plateau,
coast and ``a_max`` are then derived to fit the locked timeline and the
travel distance, taking the lowest peak acceleration of the remaining
degenerate freedom. Phase 2 is a symmetric rest-to-rest return.

The free parameters and constraints are exposed as data
(:func:`free_parameters`, :func:`constraints`) so a notebook can tabulate
them - constraints carry an explicit ``source``.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Literal

import numpy as np
from scipy.integrate import cumulative_trapezoid

G = 9.80665  # m/s^2


def _smoothstep(x: np.ndarray) -> np.ndarray:
    """C2 smootherstep 6x^5 - 15x^4 + 10x^3 on [0, 1], clipped."""
    x = np.clip(x, 0.0, 1.0)
    return x * x * x * (x * (x * 6.0 - 15.0) + 10.0)


@dataclass(frozen=True)
class ChoreographyConfig:
    """Configuration for the structural decoupled-singularity choreography."""

    total_time: float = 3.0  # s
    phase1_duration: float = 1.5  # s, equal-split hypothesis
    phase2_duration: float = 1.5  # s, equal-split hypothesis
    arc_length: float = 2.0  # m, phase-1 curved CoM path
    lateral_offset: float = 0.25  # m, diagonal sag of the curved CoM path
    return_translation: float = 0.50  # m, phase-2 return
    rotation: float = math.pi  # rad, per-phase yaw turn
    body_mass: float = 70.0  # kg
    yaw_inertia: float = 1.4  # kg m^2, Plagenhoef 1983 scaled to 70 kg
    body_compression: float = 0.030  # m, nominal rigid-door impact compression
    body_compression_min: float = 0.020  # m, literature lower bound
    body_compression_max: float = 0.050  # m, literature upper bound
    body_thickness: float = 0.28  # m, torso front-to-back depth (2x the 0.14 m torso radius)
    # Ramp times: representative values within the rate-of-force-development
    # band [ramp_min, ramp_max], the literature exclusion zone - explosive
    # voluntary force develops/releases over 50-250 ms (Maffiuletti et al.
    # 2016; Aagaard et al. 2002). The ramps are constrained to the band, not
    # pinned to a single value.
    t_give: float = 0.20  # s, start-ramp representative value
    t_letgo: float = 0.12  # s, release-ramp representative value
    ramp_min: float = 0.05  # s, RFD band lower bound
    ramp_max: float = 0.25  # s, RFD band upper bound
    a_max_ceiling: float = 5.5  # m/s^2, production limit (Mero 1992, elite + 1 SD)
    a_max_typical: float = 3.0  # m/s^2, recreational (Mero 1992)
    jerk_ceiling: float = 50.0  # m/s^3, production limit (RFD-derived)
    n_eval: int = 2000  # samples per phase


@dataclass(frozen=True)
class FreeParameter:
    """One parameter of the structural choreography model.

    Every parameter is retained. Literature and the scenario constrain
    each parameter's permissible range - the exclusion zone bounds the
    search space, it does not eliminate the parameter.
    """

    name: str
    symbol: str
    description: str
    permissible_range: str
    bounded_by: str
    unit: str


@dataclass(frozen=True)
class Constraint:
    """One constraint on the choreography. ``source`` cites its origin."""

    name: str
    kind: Literal["equality", "inequality"]
    expression: str
    source: str


@dataclass(frozen=True)
class PhaseTrajectory:
    """Solved kinematics of one phase, with its structural breakdown."""

    duration: float
    t: np.ndarray
    s: np.ndarray
    v: np.ndarray
    a: np.ndarray
    jerk: np.ndarray
    a_peak: float
    jerk_peak: float
    v_terminal: float
    t_give: float
    t_plateau: float
    t_letgo: float
    t_coast: float


@dataclass(frozen=True)
class ImpactSingularity:
    """Decoupled impact event - the body brought from v_close to rest."""

    v_close: float  # m/s
    tau_imp: float  # s
    compression: float  # m
    kinetic_energy: float  # J
    impulse: float  # N s
    a_peak: float  # m/s^2
    a_peak_g: float  # in g
    force_peak: float  # N
    yield_model: str


@dataclass(frozen=True)
class ChoreographyResult:
    """Full solved decoupled-singularity choreography."""

    config: ChoreographyConfig
    phase1: PhaseTrajectory
    phase2: PhaseTrajectory
    v_close: float
    singularity: ImpactSingularity
    feasible: bool  # whether the production limits are respected


YIELD_FACTORS: dict[str, float] = {
    "constant (rigid-plastic)": 0.50,
    "half-sine": 0.785,
    "smootherstep": 0.94,
    "linear elastic spring": 1.00,
    "Hertzian (n=1.5)": 1.25,
}


def _trapezoid(
    te: np.ndarray, t_give: float, t_plateau: float, t_letgo: float, a_max: float
) -> np.ndarray:
    """Smooth trapezoidal acceleration: give ramp, plateau, let-go ramp,
    then zero. C2 via smootherstep ramps."""
    a = np.zeros_like(te)
    g, p, ell = t_give, t_plateau, t_letgo
    rise = te < g
    a[rise] = a_max * _smoothstep(te[rise] / g)
    hold = (te >= g) & (te < g + p)
    a[hold] = a_max
    fall = (te >= g + p) & (te < g + p + ell)
    a[fall] = a_max * (1.0 - _smoothstep((te[fall] - g - p) / ell))
    return a


def _integrate(a: np.ndarray, te: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Velocity and position from acceleration, both starting at zero."""
    v = cumulative_trapezoid(a, te, initial=0.0)
    s = cumulative_trapezoid(v, te, initial=0.0)
    return v, s


def _solve_phase1(cfg: ChoreographyConfig, release_standoff: float) -> PhaseTrajectory:
    """Phase 1 - structural trapezoid. Give and let-go are literature-pinned.

    The body is released ``release_standoff`` before the door and then
    coasts that distance. The propulsion (give + plateau + let-go) must
    therefore cover ``arc_length - release_standoff``; the coast covers the
    standoff. The plateau/coast split, a_max and t_coast follow - no
    optimisation, the solution is determined by the standoff.
    """
    t1 = cfg.phase1_duration
    te = np.linspace(0.0, t1, cfg.n_eval)
    t_free = t1 - cfg.t_give - cfg.t_letgo  # plateau + coast budget
    d_contact = cfg.arc_length - release_standoff  # propulsion must cover this

    # propulsion distance decreases as the coast lengthens; find the coast
    # at which the propulsion covers exactly d_contact
    coasts = np.linspace(0.0, t_free, 160)
    s_props = np.zeros_like(coasts)
    for i, tc in enumerate(coasts):
        tp = t_free - tc
        a_unit = _trapezoid(te, cfg.t_give, tp, cfg.t_letgo, 1.0)
        _, s_unit = _integrate(a_unit, te)
        a_unit_max = cfg.arc_length / s_unit[-1]
        t_prop_end = cfg.t_give + tp + cfg.t_letgo
        s_props[i] = a_unit_max * float(np.interp(t_prop_end, te, s_unit))
    # s_props is decreasing in the coast - reverse for the interpolation
    t_coast = float(np.interp(d_contact, s_props[::-1], coasts[::-1]))
    t_coast = float(np.clip(t_coast, 0.0, t_free))
    t_plateau = t_free - t_coast

    a_unit = _trapezoid(te, cfg.t_give, t_plateau, cfg.t_letgo, 1.0)
    _, s_unit = _integrate(a_unit, te)
    a_max = cfg.arc_length / s_unit[-1]
    a = _trapezoid(te, cfg.t_give, t_plateau, cfg.t_letgo, a_max)
    v, s = _integrate(a, te)
    jerk = np.gradient(a, te)
    return PhaseTrajectory(
        duration=t1,
        t=te,
        s=s,
        v=v,
        a=a,
        jerk=jerk,
        a_peak=float(np.abs(a).max()),
        jerk_peak=float(np.abs(jerk).max()),
        v_terminal=float(v[-1]),
        t_give=cfg.t_give,
        t_plateau=float(t_plateau),
        t_letgo=cfg.t_letgo,
        t_coast=float(t_coast),
    )


def _solve_phase2(cfg: ChoreographyConfig) -> PhaseTrajectory:
    """Phase 2 - symmetric rest-to-rest return: an accelerate trapezoid then
    a mirror-image brake trapezoid, ending at rest."""
    t2 = cfg.phase2_duration
    te = np.linspace(0.0, t2, cfg.n_eval)
    half = t2 / 2.0
    p_half = half - cfg.t_give - cfg.t_letgo

    a_unit = np.zeros_like(te)
    first = te <= half
    a_unit[first] = -_trapezoid(te[first], cfg.t_give, p_half, cfg.t_letgo, 1.0)
    second = te > half
    a_unit[second] = _trapezoid(te[second] - half, cfg.t_give, p_half, cfg.t_letgo, 1.0)
    _, s_unit = _integrate(a_unit, te)
    a_p = -cfg.return_translation / s_unit[-1]  # s(t2) = -return_translation

    a = a_unit * a_p
    v, s = _integrate(a, te)
    jerk = np.gradient(a, te)
    return PhaseTrajectory(
        duration=t2,
        t=te,
        s=s,
        v=v,
        a=a,
        jerk=jerk,
        a_peak=float(np.abs(a).max()),
        jerk_peak=float(np.abs(jerk).max()),
        v_terminal=float(v[-1]),
        t_give=cfg.t_give,
        t_plateau=float(p_half),
        t_letgo=cfg.t_letgo,
        t_coast=0.0,
    )


def impact_singularity(
    v_close: float,
    tau_imp: float,
    cfg: ChoreographyConfig,
    yield_model: str = "constant (rigid-plastic)",
) -> ImpactSingularity:
    """Resolve the decoupled impact: the body decelerates v_close -> 0 over
    duration tau_imp, compressing by d = v_close * tau_imp / 2."""
    d = 0.5 * v_close * tau_imp
    factor = YIELD_FACTORS.get(yield_model, 0.50)
    a_peak = factor * v_close * v_close / d if d > 0 else 0.0
    return ImpactSingularity(
        v_close=v_close,
        tau_imp=tau_imp,
        compression=d,
        kinetic_energy=0.5 * cfg.body_mass * v_close * v_close,
        impulse=cfg.body_mass * v_close,
        a_peak=a_peak,
        a_peak_g=a_peak / G,
        force_peak=cfg.body_mass * a_peak,
        yield_model=yield_model,
    )


def solve_choreography(
    cfg: ChoreographyConfig | None = None,
    *,
    release_standoff: float = 0.0,
    tau_imp: float | None = None,
    yield_model: str = "Hertzian (n=1.5)",
) -> ChoreographyResult:
    """Solve the full structural decoupled-singularity choreography."""
    if cfg is None:
        cfg = ChoreographyConfig()
    phase1 = _solve_phase1(cfg, release_standoff)
    phase2 = _solve_phase2(cfg)
    v_close = phase1.v_terminal
    if tau_imp is None:
        tau_imp = 2.0 * cfg.body_compression / v_close
    sing = impact_singularity(v_close, tau_imp, cfg, yield_model)
    feasible = (
        phase1.a_peak <= cfg.a_max_ceiling
        and phase2.a_peak <= cfg.a_max_ceiling
        and phase1.jerk_peak <= cfg.jerk_ceiling
        and phase2.jerk_peak <= cfg.jerk_ceiling
    )
    return ChoreographyResult(
        config=cfg,
        phase1=phase1,
        phase2=phase2,
        v_close=v_close,
        singularity=sing,
        feasible=feasible,
    )


def solve_envelope(
    cfg: ChoreographyConfig | None = None,
    *,
    yield_model: str = "Hertzian (n=1.5)",
) -> tuple[ChoreographyResult, ChoreographyResult]:
    """The kinematics envelope - two bracketing solutions.

    The **no-coast** solution propels the body all the way to the door
    (release_standoff = 0). The **with-coast** solution releases it two
    torso depths back (2 x body_thickness) and lets it coast in. The actual
    motion lies between these two; the pair is the envelope.
    """
    if cfg is None:
        cfg = ChoreographyConfig()
    no_coast = solve_choreography(cfg, release_standoff=0.0, yield_model=yield_model)
    with_coast = solve_choreography(
        cfg, release_standoff=2.0 * cfg.body_thickness, yield_model=yield_model
    )
    return no_coast, with_coast


def free_parameters(cfg: ChoreographyConfig | None = None) -> list[FreeParameter]:
    """The parameters of the structural choreography model.

    None is eliminated; each is constrained to a permissible range. The
    re-parametrisation from the quintic-spline predecessor cut the count
    from 37 spline knots to these few structural parameters - literature
    then bounds them, it does not remove them.
    """
    if cfg is None:
        cfg = ChoreographyConfig()
    rfd = "RFD exclusion zone (Maffiuletti 2016, Aagaard 2002)"
    band = f"{cfg.ramp_min * 1e3:.0f} - {cfg.ramp_max * 1e3:.0f}"
    return [
        FreeParameter(
            "start ramp (give)",
            "t_give",
            "time for acceleration to rise from 0 to a_max",
            band,
            rfd,
            "ms",
        ),
        FreeParameter(
            "release ramp (let-go)",
            "t_letgo",
            "time for acceleration to fall from a_max to 0",
            band,
            rfd,
            "ms",
        ),
        FreeParameter(
            "phase durations",
            "t1, t2",
            "phase-1 and phase-2 durations",
            f"{cfg.phase1_duration:.2f} / {cfg.phase2_duration:.2f}",
            "equal-split hypothesis",
            "s",
        ),
        FreeParameter(
            "release standoff",
            "d_standoff",
            "distance from the door at which the body is released",
            f"0 - {2.0 * cfg.body_thickness:.2f}",
            "envelope variable - body geometry",
            "m",
        ),
        FreeParameter(
            "plateau / coast split",
            "t_plateau, t_coast",
            "structural durations within phase 1",
            "see run",
            "coupled: timeline + distance + standoff",
            "s",
        ),
        FreeParameter(
            "peak acceleration",
            "a_max",
            "plateau acceleration",
            f"<= {cfg.a_max_ceiling}",
            "Mero 1992 production limit",
            "m/s^2",
        ),
        FreeParameter(
            "impact-singularity duration",
            "tau_imp",
            "decoupled impact duration; d = v_close * tau / 2",
            "body compression 2-5 cm",
            "body-compression exclusion zone",
            "s",
        ),
    ]


def constraints(cfg: ChoreographyConfig | None = None) -> list[Constraint]:
    """The constraints of the structural choreography model."""
    if cfg is None:
        cfg = ChoreographyConfig()
    bc = "scenario boundary condition"
    rfd = "Maffiuletti et al. 2016; Aagaard et al. 2002 - rate of force development"
    return [
        Constraint(
            "release standoff (coasting)",
            "equality",
            f"with-coast solution: body released 2x body thickness "
            f"({2.0 * cfg.body_thickness * 1e2:.0f} cm) before the door",
            "body geometry - the actor cannot release at the door; two "
            "torso depths of standoff (torso depth ~28 cm)",
        ),
        Constraint(
            "give ramp within RFD band",
            "inequality",
            f"{cfg.ramp_min * 1e3:.0f} <= t_give <= {cfg.ramp_max * 1e3:.0f} ms",
            rfd,
        ),
        Constraint(
            "let-go ramp within RFD band",
            "inequality",
            f"{cfg.ramp_min * 1e3:.0f} <= t_letgo <= {cfg.ramp_max * 1e3:.0f} ms",
            rfd,
        ),
        Constraint(
            "phase-1 timeline",
            "equality",
            f"t_give + t_plateau + t_letgo + t_coast = {cfg.phase1_duration:.2f} s",
            bc,
        ),
        Constraint(
            "phase-1 distance", "equality", f"double-integral of a = {cfg.arc_length} m", bc
        ),
        Constraint(
            "phase-2 timeline", "equality", f"phase-2 duration = {cfg.phase2_duration:.2f} s", bc
        ),
        Constraint(
            "phase-2 distance",
            "equality",
            f"double-integral of a = -{cfg.return_translation} m",
            bc,
        ),
        Constraint("phase-2 ends at rest", "equality", "v(t2) = 0", bc),
        Constraint(
            "peak acceleration limit",
            "inequality",
            f"a_max <= {cfg.a_max_ceiling} m/s^2",
            "Mero, Komi & Gregor 1992 - peak CoM acceleration",
        ),
        Constraint("peak jerk limit", "inequality", f"|jerk| <= {cfg.jerk_ceiling} m/s^3", rfd),
        Constraint(
            "impact-duration ceiling",
            "inequality",
            f"tau_imp = 2 d / v_close, d <= {cfg.body_compression_max * 1e2:.0f} cm",
            "body-compression range - Lobdell 1973; Kroell 1971; Kemper et al. 2014",
        ),
    ]


__all__ = [
    "G",
    "YIELD_FACTORS",
    "ChoreographyConfig",
    "ChoreographyResult",
    "Constraint",
    "FreeParameter",
    "ImpactSingularity",
    "PhaseTrajectory",
    "constraints",
    "free_parameters",
    "impact_singularity",
    "solve_choreography",
    "solve_envelope",
]
