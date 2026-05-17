"""Decoupled-singularity smooth-choreography kinematics.

The corridor incident's second-pass kinematic model. The choreography is a
two-phase smooth trajectory - a phase-1 approach, a decoupled impact
singularity, and a phase-2 return - with the tangential acceleration ``a(t)``
a **quintic spline** through the linear-prototype control points. At each
control point the value, the 1st derivative (jerk) and the 2nd derivative
(snap) are free; the optimiser sets them to minimise the integral of jerk
squared subject to boundary conditions and biomechanical production limits
drawn from literature - the exclusion zones, here enforced as hard
inequality constraints.

The free parameters and the constraints are exposed as data
(:func:`free_parameters`, :func:`constraints`) so a notebook can tabulate
them - constraints carry an explicit ``source`` citing the literature or
the scenario definition.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Literal

import numpy as np
from scipy.interpolate import BPoly
from scipy.optimize import LinearConstraint, minimize

G = 9.80665  # m/s^2

# Control points inherited from the kinematics linear prototype, as fractions
# of the phase duration. Phase 1: start, start-jerk end, constant end,
# release end, coast end, contact. Phase 2: start, reverse-jerk end, hold
# end, decel end, hold end, rest.
PHASE1_CONTROL_FRACTIONS: tuple[float, ...] = (0.0, 0.20, 0.57, 0.73, 0.90, 1.0)
PHASE2_CONTROL_FRACTIONS: tuple[float, ...] = (0.0, 0.15, 0.35, 0.65, 0.85, 1.0)

# Phase-2 duration is locked by the 180 deg rotation: the midpoint of the
# elite and population yaw-rate floors (Hodgson, Lewis & Drury 2008).
_OMEGA_POPULATION = 3.5  # rad/s
_OMEGA_ELITE = 5.5  # rad/s
_PHASE2_LOCKED = 0.5 * (2.0 * math.pi / _OMEGA_POPULATION + 2.0 * math.pi / _OMEGA_ELITE)


@dataclass(frozen=True)
class ChoreographyConfig:
    """Locked configuration for the decoupled-singularity choreography."""

    total_time: float = 3.0  # s
    arc_length: float = 2.0  # m, phase-1 curved CoM path
    return_translation: float = 0.50  # m, phase-2 return
    rotation: float = math.pi  # rad, per-phase yaw turn
    body_mass: float = 70.0  # kg
    yaw_inertia: float = 1.4  # kg m^2, Plagenhoef 1983 scaled to 70 kg
    body_compression: float = 0.030  # m, nominal rigid-door impact compression
    body_compression_min: float = 0.020  # m, literature lower bound (yield study)
    body_compression_max: float = 0.050  # m, literature upper bound (yield study)
    phase2_duration: float = _PHASE2_LOCKED  # s, locked by the rotation constraint
    a_max_ceiling: float = 5.5  # m/s^2, production limit (Mero 1992, elite + 1 SD)
    a_max_typical: float = 3.0  # m/s^2, recreational (Mero 1992)
    jerk_ceiling: float = 50.0  # m/s^3, production limit (RFD-derived)
    n_knots: int = 6  # control points per phase
    n_eval: int = 400  # integration / sampling resolution per phase

    @property
    def phase1_duration(self) -> float:
        """Phase-1 duration - the remainder after the locked phase 2."""
        return self.total_time - self.phase2_duration


@dataclass(frozen=True)
class FreeParameter:
    """One family of optimisation variables of the choreography QP."""

    name: str
    symbol: str
    description: str
    count: int  # number of scalar variables in this family
    lower: float
    upper: float
    unit: str


@dataclass(frozen=True)
class Constraint:
    """One constraint on the choreography optimisation.

    ``source`` cites where the constraint comes from - a literature
    reference for the production limits, or the scenario definition for the
    boundary conditions.
    """

    name: str
    kind: Literal["equality", "inequality"]
    expression: str  # human-readable, e.g. "|a(t)| <= 5.5 m/s^2"
    source: str


@dataclass(frozen=True)
class PhaseTrajectory:
    """Solved kinematics of one phase."""

    duration: float
    t: np.ndarray
    s: np.ndarray
    v: np.ndarray
    a: np.ndarray
    jerk: np.ndarray
    a_peak: float
    jerk_peak: float
    v_terminal: float


@dataclass(frozen=True)
class ImpactSingularity:
    """Decoupled impact event - the body brought from v_close to rest."""

    v_close: float  # m/s
    tau_imp: float  # s, the impact-singularity duration parameter
    compression: float  # m
    kinetic_energy: float  # J
    impulse: float  # N s
    a_peak: float  # m/s^2, peak deceleration (yield-model dependent)
    a_peak_g: float  # in g
    force_peak: float  # N
    yield_model: str


@dataclass(frozen=True)
class ChoreographyResult:
    """Full solved decoupled-singularity choreography."""

    config: ChoreographyConfig
    phase1: PhaseTrajectory
    phase2: PhaseTrajectory
    v_close: float  # m/s, emergent phase-1 terminal velocity
    singularity: ImpactSingularity
    bounds_active: bool  # whether any production limit was binding


# yield-shape peak factor: a_peak = factor * v_close^2 / d
YIELD_FACTORS: dict[str, float] = {
    "constant (rigid-plastic)": 0.50,
    "half-sine": 0.785,
    "smootherstep": 0.94,
    "linear elastic spring": 1.00,
    "Hertzian (n=1.5)": 1.25,
}


def _phase_basis(knot_times: np.ndarray, n_eval: int) -> dict:
    """Probe the quintic-spline machinery for one phase.

    The acceleration a(t) is a quintic spline whose per-knot data is
    (value, jerk, snap). The spline is linear in that data, so a(t),
    jerk(t), v(t) and s(t) are all linear maps of the variable vector.
    Returns the basis matrices and the jerk-squared quadratic form.
    """
    n = len(knot_times)
    nvar = 3 * n  # value, jerk, snap per knot
    duration = float(knot_times[-1])
    te = np.linspace(0.0, duration, n_eval)
    dte = te[1] - te[0]

    a_basis = np.zeros((nvar, n_eval))
    jerk_basis = np.zeros((nvar, n_eval))
    v_basis = np.zeros((nvar, n_eval))
    s_basis = np.zeros((nvar, n_eval))
    for k in range(nvar):
        e = np.zeros(nvar)
        e[k] = 1.0
        y = e.reshape(3, n).T  # (n, 3): value, 1st deriv, 2nd deriv per knot
        spl = BPoly.from_derivatives(knot_times, y)
        cv = spl.antiderivative()
        cs = cv.antiderivative()
        a_basis[k] = spl(te)
        jerk_basis[k] = spl(te, 1)
        v_basis[k] = cv(te) - cv(0.0)
        s_basis[k] = cs(te) - cs(0.0) - cv(0.0) * te
    hessian = (jerk_basis @ jerk_basis.T) * dte + 1e-9 * np.eye(nvar)
    return {
        "te": te,
        "n": n,
        "nvar": nvar,
        "duration": duration,
        "a": a_basis,
        "jerk": jerk_basis,
        "v": v_basis,
        "s": s_basis,
        "H": hessian,
    }


def _solve_phase(
    knot_times: np.ndarray,
    equalities: list[tuple[np.ndarray, float]],
    cfg: ChoreographyConfig,
) -> tuple[np.ndarray, dict, bool]:
    """Quintic-spline jerk-minimal QP for one phase.

    Minimises the integral of jerk squared subject to the equality boundary
    conditions and the production-limit inequalities (|a| <= a_max_ceiling,
    |jerk| <= jerk_ceiling) - the exclusion zones, banned by construction.
    """
    basis = _phase_basis(knot_times, cfg.n_eval)
    nvar, hessian = basis["nvar"], basis["H"]

    a_eq = np.array([row for row, _ in equalities])
    b_eq = np.array([val for _, val in equalities])

    # equality-only KKT solution as a warm start
    n_c = len(b_eq)
    kkt = np.block([[hessian, a_eq.T], [a_eq, np.zeros((n_c, n_c))]])
    x0 = np.linalg.solve(kkt, np.concatenate([np.zeros(nvar), b_eq]))[:nvar]

    # production-limit inequalities, sampled along the phase
    samp = slice(None, None, 5)
    a_s = basis["a"][:, samp].T
    j_s = basis["jerk"][:, samp].T
    a_ineq = np.vstack([a_s, -a_s, j_s, -j_s])
    b_ineq = np.concatenate(
        [
            np.full(a_s.shape[0], cfg.a_max_ceiling),
            np.full(a_s.shape[0], cfg.a_max_ceiling),
            np.full(j_s.shape[0], cfg.jerk_ceiling),
            np.full(j_s.shape[0], cfg.jerk_ceiling),
        ]
    )

    cons = [
        LinearConstraint(a_eq, b_eq, b_eq),
        LinearConstraint(a_ineq, -np.inf, b_ineq),
    ]
    res = minimize(
        lambda x: 0.5 * x @ hessian @ x,
        x0,
        jac=lambda x: hessian @ x,
        hess=lambda x: hessian,
        method="trust-constr",
        constraints=cons,
        options={"maxiter": 400, "gtol": 1e-9, "xtol": 1e-10},
    )
    x = res.x
    active = bool(np.any(a_ineq @ x > b_ineq - 1e-3))
    return x, basis, active


def _phase_trajectory(x: np.ndarray, basis: dict) -> PhaseTrajectory:
    a = x @ basis["a"]
    jerk = x @ basis["jerk"]
    v = x @ basis["v"]
    s = x @ basis["s"]
    return PhaseTrajectory(
        duration=basis["duration"],
        t=basis["te"],
        s=s,
        v=v,
        a=a,
        jerk=jerk,
        a_peak=float(np.abs(a).max()),
        jerk_peak=float(np.abs(jerk).max()),
        v_terminal=float(v[-1]),
    )


def impact_singularity(
    v_close: float,
    tau_imp: float,
    cfg: ChoreographyConfig,
    yield_model: str = "constant (rigid-plastic)",
) -> ImpactSingularity:
    """Resolve the decoupled impact for a closing velocity and duration.

    The body decelerates v_close -> 0 over the singularity duration
    ``tau_imp``; the compression follows as d = v_close * tau_imp / 2 and
    the peak deceleration scales with the yield-shape factor.
    """
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
    tau_imp: float | None = None,
    yield_model: str = "Hertzian (n=1.5)",
) -> ChoreographyResult:
    """Solve the full decoupled-singularity choreography.

    Phase 1: rest -> door, terminal velocity v_close free (emergent).
    Phase 2: rest -> return_translation back -> rest.
    The impact singularity is resolved at the chosen ``tau_imp`` (defaulting
    to the upper bound - the longest, softest impact the compression allows).
    """
    if cfg is None:
        cfg = ChoreographyConfig()

    t1, t2 = cfg.phase1_duration, cfg.phase2_duration
    kt1 = np.array(PHASE1_CONTROL_FRACTIONS) * t1
    kt2 = np.array(PHASE2_CONTROL_FRACTIONS) * t2

    # phase 1: a(0)=0, s(t1)=arc_length, a(t1)=0; v(t1)=v_close free
    b1 = _phase_basis(kt1, cfg.n_eval)
    eq1 = [
        (b1["a"][:, 0].copy(), 0.0),
        (b1["s"][:, -1].copy(), cfg.arc_length),
        (b1["a"][:, -1].copy(), 0.0),
    ]
    x1, basis1, act1 = _solve_phase(kt1, eq1, cfg)
    phase1 = _phase_trajectory(x1, basis1)

    # phase 2: a(0)=0, s(t2)=-return, v(t2)=0, a(t2)=0
    b2 = _phase_basis(kt2, cfg.n_eval)
    eq2 = [
        (b2["a"][:, 0].copy(), 0.0),
        (b2["s"][:, -1].copy(), -cfg.return_translation),
        (b2["v"][:, -1].copy(), 0.0),
        (b2["a"][:, -1].copy(), 0.0),
    ]
    x2, basis2, act2 = _solve_phase(kt2, eq2, cfg)
    phase2 = _phase_trajectory(x2, basis2)

    v_close = phase1.v_terminal
    if tau_imp is None:
        # impact duration consistent with the nominal body compression:
        # d = v_close * tau / 2  ->  tau = 2 d / v_close
        tau_imp = 2.0 * cfg.body_compression / v_close
    sing = impact_singularity(v_close, tau_imp, cfg, yield_model)
    return ChoreographyResult(
        config=cfg,
        phase1=phase1,
        phase2=phase2,
        v_close=v_close,
        singularity=sing,
        bounds_active=act1 or act2,
    )


def free_parameters(
    cfg: ChoreographyConfig | None = None,
    v_close: float = 2.45,
) -> list[FreeParameter]:
    """The optimisation variables of the choreography QP.

    ``v_close`` (representative closing velocity) sets the tau_imp bounds,
    which derive from the body-compression range.
    """
    if cfg is None:
        cfg = ChoreographyConfig()
    n = cfg.n_knots
    jc, ac = cfg.jerk_ceiling, cfg.a_max_ceiling
    return [
        FreeParameter(
            "control-point acceleration",
            "a_i",
            "tangential acceleration at each linear-prototype control point, per phase",
            2 * n,
            -ac,
            ac,
            "m/s^2",
        ),
        FreeParameter(
            "control-point jerk",
            "j_i",
            "1st derivative of acceleration at each control point, per phase",
            2 * n,
            -jc,
            jc,
            "m/s^3",
        ),
        FreeParameter(
            "control-point snap",
            "s_i",
            "2nd derivative of acceleration at each control point, per phase",
            2 * n,
            -np.inf,
            np.inf,
            "m/s^4",
        ),
        FreeParameter(
            "impact-singularity duration",
            "tau_imp",
            "duration of the decoupled impact; d = v_close * tau / 2, bounded "
            "by the body-compression range",
            1,
            2.0 * cfg.body_compression_min / v_close,
            2.0 * cfg.body_compression_max / v_close,
            "s",
        ),
    ]


def constraints(cfg: ChoreographyConfig | None = None) -> list[Constraint]:
    """The equality and inequality constraints of the choreography QP.

    Equalities are the scenario boundary conditions; inequalities are the
    biomechanical production limits - the exclusion zones - each citing its
    literature source.
    """
    if cfg is None:
        cfg = ChoreographyConfig()
    bc = "scenario boundary condition"
    return [
        Constraint("phase-1 smooth start", "equality", "a(0) = 0", bc),
        Constraint("phase-1 reaches the door", "equality", f"s(t1) = {cfg.arc_length} m", bc),
        Constraint("phase-1 released at contact", "equality", "a(t1) = 0", bc),
        Constraint("phase-2 smooth push-off", "equality", "a(0) = 0", bc),
        Constraint(
            "phase-2 return distance", "equality", f"s(t2) = -{cfg.return_translation} m", bc
        ),
        Constraint("phase-2 ends at rest", "equality", "v(t2) = 0", bc),
        Constraint("phase-2 zero end acceleration", "equality", "a(t2) = 0", bc),
        Constraint(
            "peak acceleration limit",
            "inequality",
            f"|a(t)| <= {cfg.a_max_ceiling} m/s^2",
            "Mero, Komi & Gregor 1992 - peak CoM acceleration, elite + 1 SD",
        ),
        Constraint(
            "peak jerk limit",
            "inequality",
            f"|jerk(t)| <= {cfg.jerk_ceiling} m/s^3",
            "Maffiuletti et al. 2016; Aagaard et al. 2002 - rate of force "
            "development (jerk = force rate / mass)",
        ),
        Constraint(
            "impact-duration ceiling",
            "inequality",
            f"tau_imp = 2 d / v_close,  d <= {cfg.body_compression_max * 1e2:.0f} cm",
            "body-compression range - Lobdell 1973; Kroell 1971; Kemper et al. 2014",
        ),
    ]


__all__ = [
    "G",
    "PHASE1_CONTROL_FRACTIONS",
    "PHASE2_CONTROL_FRACTIONS",
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
]
