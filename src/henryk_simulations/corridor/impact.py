"""Back-impact dynamics - lumped-parameter posterior-thorax model.

Notebook 02's impact model. The body, delivered to the elevator door by
notebook 01's kinematics envelope at a closing velocity ``v_close``, strikes
the rigid door back-first. The model is lumped-parameter throughout - no
finite-element mesh - and answers one question: could the impact fracture
ribs or vertebrae.

The model has four parts, all here:

- **Body segments** - de Leva (1996) adjusted Zatsiorsky-Seluyanov segment
  inertia for a 70 kg adult, used to separate the mass behind the back from
  the limbs that whip on their joints (the effective impacting mass).
- **Contact patches** - the posterior profile meets the flat door in a
  sequence: scapulae first, then the mid-thoracic ribs, then the lower back.
  The contact area builds up over the impact and sets the pressure.
- **Posterior-thorax chain** - a 5-DOF Lobdell-style mass-spring-damper
  chain (skin, scapula, ribcage, organ, spine) struck against the rigid
  door through a Hertzian contact with an elastic-plastic yield plateau.
- **Fracture thresholds** - literature force and deflection corridors; the
  computed peaks are scored against them.

The door is modelled **rigid** - the worst case for the body. A real door
flexes (first panel mode ~37 Hz) and would lower the load; an FE-coupled
door is left to a later notebook.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from scipy.integrate import solve_ivp

from henryk_simulations.corridor.choreography import ChoreographyConfig, solve_envelope

G = 9.80665  # m/s^2

# de Leva (1996) male segment mass, fraction of total body mass. The trunk
# is split into thorax, abdomen and pelvis; limbs are per single segment.
DE_LEVA_MALE: dict[str, tuple[str, int, float]] = {
    "head": ("back", 1, 0.0694),
    "thorax": ("back", 1, 0.1596),
    "abdomen": ("back", 1, 0.1633),
    "pelvis": ("back", 1, 0.1117),
    "upper arm": ("limb", 2, 0.0271),
    "forearm": ("limb", 2, 0.0162),
    "hand": ("limb", 2, 0.0061),
    "thigh": ("limb", 2, 0.1416),
    "shank": ("limb", 2, 0.0433),
    "foot": ("limb", 2, 0.0137),
}


@dataclass(frozen=True)
class ImpactConfig:
    """Configuration for the back-impact dynamics model."""

    body_mass: float = 70.0  # kg
    body_height: float = 1.68  # m
    # subject demographics - sex and age shift the injury thresholds in
    # injuries.py through tolerance_factor. Sex is "F" or "M"; age in years,
    # None - assume a standard adult (the mixed-cadaver reference age).
    subject_gender: Literal["F", "M"] = "F"  # subject sex - F or M
    subject_age: float | None = None  # years; None - standard adult
    # 5-DOF posterior-thorax chain (Lobdell-style anatomical layers). The
    # masses sum to body_mass - the chain lumps the whole body, the rigid
    # worst case; the effective-mass analysis shows the real backing mass.
    m_skin: float = 1.5  # kg, outer skin and posterior flesh
    m_scapula: float = 3.0  # kg, scapula and immediate bone
    m_ribcage: float = 10.0  # kg, rib cage
    m_organ: float = 15.0  # kg, thoracic and abdominal organs
    m_spine: float = 40.5  # kg, spine and the rest of the body bulk
    # interface stiffness, N/m (notebook 06 anatomical chain)
    k_skin: float = 2.0e5  # 200 N/mm, posterior skin and fat
    k_scapula: float = 8.0e5  # 800 N/mm, scapula-rib articulation
    k_rib: float = 3.5e5  # 350 N/mm, rib cage - the injury interface
    k_spine: float = 6.0e5  # 600 N/mm, organ-spine
    # interface damping, N s/m
    c_skin: float = 800.0
    c_scapula: float = 1500.0
    c_rib: float = 1200.0
    c_spine: float = 2000.0
    # skin-to-door contact: Hunt-Crossley Hertzian contact, the door rigid
    k_contact: float = 5.0e6  # N/m^n, contact stiffness (scapular patch)
    n_contact: float = 1.5  # Hertzian exponent
    lambda_hc: float = 1.5  # s/m, Hunt-Crossley damping
    yield_force: float = 9000.0  # N, elastic-plastic yield plateau (plastic body deformation)
    # posterior contact patches - exponential area build-up A(t)
    area_initial: float = 0.010  # m^2, first contact (scapula tips), ~100 cm^2
    area_final: float = 0.060  # m^2, full posterior thorax, ~600 cm^2
    area_tau: float = 0.015  # s, contact-area build-up time constant
    n_ribs_span: int = 7  # ribs spanned by the full-area back contact
    t_max: float = 0.15  # s, impact integration window
    n_eval: int = 1500  # output samples


@dataclass(frozen=True)
class BodySegment:
    """One de Leva body segment."""

    name: str
    group: str  # "back" (behind the contact) or "limb" (whips on joints)
    count: int  # 1 or 2 (paired segments)
    mass_fraction: float  # per single segment, fraction of body mass
    mass: float  # kg, total for the count


@dataclass(frozen=True)
class EffectiveMass:
    """The mass actually behind the back-first contact.

    The back segments (head, thorax, abdomen, pelvis) lie directly behind
    the contact and couple at once. The limbs hang on joints; over the
    ~40 ms impact they couple only partly. The real impacting mass lies
    between the two bounds - an envelope, as in notebook 01.
    """

    m_back: float  # kg, head + trunk - couples immediately
    m_limbs: float  # kg, arms + legs - whip on the joints
    m_eff_low: float  # kg, limbs fully decoupled
    m_eff_high: float  # kg, whole body rigid (the chain default)


@dataclass(frozen=True)
class ContactPatch:
    """One posterior contact region, in its order of contact."""

    name: str
    order: int
    area: float  # m^2, this region's contribution
    note: str


# the posterior profile meets a flat door in this order
POSTERIOR_PATCHES: tuple[ContactPatch, ...] = (
    ContactPatch("scapulae", 1, 0.010, "shoulder blades protrude ~3-4 cm, strike first"),
    ContactPatch("mid-thoracic ribs", 2, 0.030, "kyphosis apex T5-T6, ribs flatten onto the door"),
    ContactPatch("lower thorax / lumbar", 3, 0.020, "lumbar lordosis is recessed, contacts last"),
)


@dataclass(frozen=True)
class ImpactDynamicsResult:
    """Solved back-impact - force history and peaks."""

    config: ImpactConfig
    v_close: float  # m/s, incoming closing velocity
    t: np.ndarray  # s
    f_contact: np.ndarray  # N, skin-to-door contact force (elastic demand)
    f_contact_capped: np.ndarray  # N, contact force with the yield plateau
    f_rib: np.ndarray  # N, force at the ribcage interface
    f_spine: np.ndarray  # N, force at the organ-spine interface
    penetration: np.ndarray  # m, skin compression into the door
    rib_compression: np.ndarray  # m, rib cage compression (ribcage-organ interface)
    area: np.ndarray  # m^2, contact area build-up
    pressure: np.ndarray  # Pa, capped contact force over contact area
    peak_force: float  # N, peak elastic contact force (the demand)
    peak_rib_force: float  # N, peak ribcage-interface force
    peak_spine_force: float  # N, peak organ-spine-interface force
    peak_penetration: float  # m
    peak_rib_compression: float  # m
    peak_pressure: float  # Pa
    ribs_engaged: float  # ribs sharing the load at peak force
    per_rib_force: float  # N, peak force divided over the engaged ribs
    plastic_deformation: float  # m, penetration past the yield point
    yields: bool  # whether the elastic force crosses the yield plateau
    kinetic_energy: float  # J, incoming


@dataclass(frozen=True)
class FractureThreshold:
    """One literature fracture / injury threshold. ``source`` cites it."""

    name: str
    value: float
    unit: str
    source: str


@dataclass(frozen=True)
class FractureVerdict:
    """A computed quantity scored against a fracture threshold."""

    quantity: str
    value: float
    threshold: float
    unit: str
    source: str
    verdict: str  # "fracture", "borderline", or "no fracture"


def body_segments(cfg: ImpactConfig | None = None) -> list[BodySegment]:
    """The de Leva (1996) body-segment breakdown for the configured mass."""
    if cfg is None:
        cfg = ImpactConfig()
    segments = []
    for name, (group, count, frac) in DE_LEVA_MALE.items():
        segments.append(BodySegment(name, group, count, frac, count * frac * cfg.body_mass))
    return segments


def effective_impact_mass(cfg: ImpactConfig | None = None) -> EffectiveMass:
    """The effective impacting mass behind the back-first contact.

    The back segments couple immediately; the limbs whip on their joints.
    The real impacting mass is bracketed by ``m_eff_low`` (limbs free) and
    ``m_eff_high`` (whole body rigid).
    """
    if cfg is None:
        cfg = ImpactConfig()
    segs = body_segments(cfg)
    m_back = sum(s.mass for s in segs if s.group == "back")
    m_limbs = sum(s.mass for s in segs if s.group == "limb")
    return EffectiveMass(
        m_back=m_back,
        m_limbs=m_limbs,
        m_eff_low=m_back,
        m_eff_high=m_back + m_limbs,
    )


def contact_area(t: np.ndarray, cfg: ImpactConfig | None = None) -> np.ndarray:
    """Posterior contact area over the impact - an exponential build-up.

    Contact starts at the scapulae and spreads over the thorax;
    ``A(t) = A_initial + (A_final - A_initial)(1 - exp(-t / tau))``.
    """
    if cfg is None:
        cfg = ImpactConfig()
    grow = 1.0 - np.exp(-np.maximum(t, 0.0) / cfg.area_tau)
    return cfg.area_initial + (cfg.area_final - cfg.area_initial) * grow


def ribs_engaged(area: float, cfg: ImpactConfig | None = None) -> float:
    """Ribs sharing the contact load at the given contact area."""
    if cfg is None:
        cfg = ImpactConfig()
    fraction = float(np.clip(area / cfg.area_final, 0.0, 1.0))
    return max(1.0, fraction * cfg.n_ribs_span)


def solve_impact(
    cfg: ImpactConfig | None = None,
    v_close: float = 2.74,
    *,
    yield_force: float | None = None,
) -> ImpactDynamicsResult:
    """Solve the 5-DOF posterior-thorax chain striking the rigid door.

    The chain (skin, scapula, ribcage, organ, spine) moves at ``v_close``
    into a rigid wall. The skin-to-door contact is Hertzian with
    Hunt-Crossley damping. ``yield_force`` caps the contact force at the
    elastic-plastic plateau; the uncapped (elastic) force is the demand the
    impact would generate and is what the fracture verdict scores.
    """
    if cfg is None:
        cfg = ImpactConfig()
    if yield_force is None:
        yield_force = cfg.yield_force

    masses = np.array([cfg.m_skin, cfg.m_scapula, cfg.m_ribcage, cfg.m_organ, cfg.m_spine])
    k = np.array([cfg.k_skin, cfg.k_scapula, cfg.k_rib, cfg.k_spine])
    c = np.array([cfg.c_skin, cfg.c_scapula, cfg.c_rib, cfg.c_spine])

    def contact_force(x1: float, v1: float) -> float:
        if x1 >= 0.0:
            return 0.0
        f = cfg.k_contact * (-x1) ** cfg.n_contact * (1.0 + cfg.lambda_hc * (-v1))
        return min(max(f, 0.0), yield_force)

    def rhs(_t: float, y: np.ndarray) -> np.ndarray:
        x = y[0::2]
        v = y[1::2]
        f_c = contact_force(x[0], v[0])
        # interface force pulling mass i toward mass i+1
        f_int = k * (x[1:] - x[:-1]) + c * (v[1:] - v[:-1])
        a = np.empty(5)
        a[0] = (f_c + f_int[0]) / masses[0]
        a[1:4] = (-f_int[:-1] + f_int[1:]) / masses[1:4]
        a[4] = -f_int[3] / masses[4]
        dy = np.empty(10)
        dy[0::2] = v
        dy[1::2] = a
        return dy

    y0 = np.zeros(10)
    y0[1::2] = -v_close  # all masses moving toward the door
    te = np.linspace(0.0, cfg.t_max, cfg.n_eval)
    sol = solve_ivp(
        rhs,
        (0.0, cfg.t_max),
        y0,
        t_eval=te,
        method="RK45",
        rtol=1e-8,
        atol=1e-10,
        max_step=2e-5,
    )
    x = sol.y[0::2]
    v = sol.y[1::2]

    pen = np.maximum(-x[0], 0.0)
    f_elastic = np.where(
        x[0] < 0.0,
        np.maximum(cfg.k_contact * pen**cfg.n_contact * (1.0 + cfg.lambda_hc * (-v[0])), 0.0),
        0.0,
    )
    f_capped = np.minimum(f_elastic, yield_force)
    f_rib = np.abs(k[2] * (x[3] - x[2]) + c[2] * (v[3] - v[2]))
    f_spine = np.abs(k[3] * (x[4] - x[3]) + c[3] * (v[4] - v[3]))
    rib_comp = np.maximum(x[2] - x[3], 0.0)

    area = contact_area(sol.t, cfg)
    pressure = f_capped / area

    peak_force = float(f_elastic.max())
    i_peak = int(np.argmax(f_elastic))
    ribs = ribs_engaged(float(area[i_peak]), cfg)
    yields = peak_force > yield_force
    pen_yield = (yield_force / cfg.k_contact) ** (1.0 / cfg.n_contact)
    plastic = max(0.0, float(pen.max()) - pen_yield) if yields else 0.0

    return ImpactDynamicsResult(
        config=cfg,
        v_close=v_close,
        t=sol.t,
        f_contact=f_elastic,
        f_contact_capped=f_capped,
        f_rib=f_rib,
        f_spine=f_spine,
        penetration=pen,
        rib_compression=rib_comp,
        area=area,
        pressure=pressure,
        peak_force=peak_force,
        peak_rib_force=float(f_rib.max()),
        peak_spine_force=float(f_spine.max()),
        peak_penetration=float(pen.max()),
        peak_rib_compression=float(rib_comp.max()),
        peak_pressure=float(pressure.max()),
        ribs_engaged=ribs,
        per_rib_force=peak_force / ribs,
        plastic_deformation=plastic,
        yields=yields,
        kinetic_energy=0.5 * cfg.body_mass * v_close**2,
    )


def solve_impact_envelope(
    cfg: ImpactConfig | None = None,
) -> tuple[ImpactDynamicsResult, ImpactDynamicsResult]:
    """The impact envelope - the back-impact at notebook 01's two v_close.

    Notebook 01's kinematics envelope brackets the closing velocity: the
    no-coast solution is faster, the with-coast solution slower. The impact
    is solved at both; the real event lies between.
    """
    if cfg is None:
        cfg = ImpactConfig()
    no_coast, with_coast = solve_envelope(ChoreographyConfig())
    fast = solve_impact(cfg, no_coast.v_close)
    slow = solve_impact(cfg, with_coast.v_close)
    return fast, slow


def fracture_thresholds() -> list[FractureThreshold]:
    """Literature fracture and injury thresholds for posterior-thorax impact."""
    return [
        FractureThreshold(
            "single rib, three-point bending",
            3000.0,
            "N",
            "isolated-rib bending tests - fracture 2-5 kN, ~3 kN at 25% risk",
        ),
        FractureThreshold(
            "rib fracture per rib (AIS 2+)",
            1600.0,
            "N",
            "Viano 1989 - 1.6 kN per loaded rib at AIS 2+",
        ),
        FractureThreshold(
            "posterior thorax tolerance",
            6900.0,
            "N",
            "Kemper et al. 2014 - rear-torso impact, 6.9-10.5 kN produces "
            "rib and costo-vertebral injury",
        ),
        FractureThreshold(
            "vertebral body compression",
            5000.0,
            "N",
            "thoracolumbar biomechanics - 4-8 kN healthy vertebral body, 2-3 kN "
            "osteoporotic; back impact loads the spine in extension, not compression",
        ),
        FractureThreshold(
            "thoracic deflection (AIS 3+)",
            0.025,
            "m",
            "Cavanaugh 1990 - AIS 3+ thoracic injury at 25 mm deflection",
        ),
    ]


def assess_fracture(
    result: ImpactDynamicsResult,
    thresholds: list[FractureThreshold] | None = None,
) -> list[FractureVerdict]:
    """Score the impact's computed peaks against the fracture thresholds.

    A quantity within 20% below its threshold is reported as borderline.
    The spinal check uses the organ-spine interface force, the conservative
    load reaching the spine; back-first impact loads the spine in extension,
    not axial compression, so the vertebral check is an upper bound.
    """
    if thresholds is None:
        thresholds = fracture_thresholds()
    by_name = {t.name: t for t in thresholds}

    def verdict(value: float, threshold: float) -> str:
        if value >= threshold:
            return "fracture"
        if value >= 0.8 * threshold:
            return "borderline"
        return "no fracture"

    checks = [
        ("peak contact force", result.peak_force, "posterior thorax tolerance"),
        ("per-rib contact force", result.per_rib_force, "single rib, three-point bending"),
        ("per-rib contact force (AIS 2+)", result.per_rib_force, "rib fracture per rib (AIS 2+)"),
        ("rib compression", result.peak_rib_compression, "thoracic deflection (AIS 3+)"),
        ("spinal interface force", result.peak_spine_force, "vertebral body compression"),
    ]
    out = []
    for quantity, value, threshold_name in checks:
        thr = by_name[threshold_name]
        out.append(
            FractureVerdict(
                quantity=quantity,
                value=value,
                threshold=thr.value,
                unit=thr.unit,
                source=thr.source,
                verdict=verdict(value, thr.value),
            )
        )
    return out


__all__ = [
    "DE_LEVA_MALE",
    "G",
    "POSTERIOR_PATCHES",
    "BodySegment",
    "ContactPatch",
    "EffectiveMass",
    "FractureThreshold",
    "FractureVerdict",
    "ImpactConfig",
    "ImpactDynamicsResult",
    "assess_fracture",
    "body_segments",
    "contact_area",
    "effective_impact_mass",
    "fracture_thresholds",
    "ribs_engaged",
    "solve_impact",
    "solve_impact_envelope",
]
