"""Injury prediction from impact metrics.

A literature-grounded reference table that maps the metrics of a back-first
blunt impact to the posterior thorax onto the injuries it predicts. Every
row carries an Abbreviated Injury Scale (AIS) severity, a tissue class, a
probability band, a description of why it sits in that band, and a cited
source.

The probability bands are assessed for the corridor back-impact scenario -
a 70 kg body, 2.4-2.7 m/s closing speed, 194-262 J of delivered kinetic
energy, a peak contact force of 2.4-6.4 kN across the impact-model range,
spread over a ~200-300 cm2 posterior-thorax patch giving a peak contact
pressure of roughly 80-320 kPa:

- **certain** - the metric is far above the injury's onset; it cannot be avoided
- **highly probable** - the metric clears the onset across the impact range
- **moderately probable** - the metric straddles the onset; the outcome turns
  on the contact stiffness and the exact load path
- **low probability** - the onset sits above the impact range, reached only
  at its stiff-model extreme
- **impossible** - the onset is far above anything this impact develops

Three key indicators are used:

- **energy** is the firmest - the delivered kinetic energy is ``0.5 m v^2``
  and does not depend on the impact model. Rib fracture has a clear energy
  threshold (~60 J) in the cadaver literature.
- **force** is model-dependent - the same impact peaks at a different force
  under a different contact stiffness. The structural and bony injuries key
  off the peak contact force.
- **pressure** governs the superficial soft-tissue injuries. A given energy
  or force spread over a wide contact area does little; concentrated over a
  small one it bruises and abrades. The pressure onsets are anchored to the
  behind-armor-blunt-trauma contact-stress scale (roughly 126 / 178 / 241
  kPa for low / moderate / high blunt impact) and are indicative - the
  literature gives no sharp kPa fracture threshold, so only the surface
  soft-tissue rows key off pressure.

Sex and age
-----------

The onset thresholds in the table are a mixed-cadaver baseline - a standard
adult, sex unspecified, near the young-adult bone-strength peak. Two
demographic factors shift them, and the biomechanical literature is clear
that they act differently and to very different degrees:

- **Age is the dominant factor, and it acts on bone.** Rib cortical bone
  loses roughly 12% of its failure strain per decade of adult ageing; its
  ultimate strength, stiffness, fracture toughness and energy-to-fracture
  all fall away from the young-adult peak (25-40 yr). A 70-year-old ribcage
  tolerates only about two-thirds of the impact speed a 30-year-old does at
  the same fracture risk - the energy tolerance roughly halves. Vertebral
  bone follows bone mineral density, which declines steadily with age and
  faster after the menopause. Soft tissue, viscera and ligament are far
  less age-sensitive.
- **Sex is a secondary factor, and it is structural, not material.** Rib
  cortical *bone material* shows no significant sex difference in failure
  strain. The sex difference is geometry: female ribs are thinner, smaller
  in cross-section and thin faster with age, so a female ribcage fractures
  at a lower *force* than a male one of the same loading. The gap is modest
  in young adults and widens after about 40; for vertebral bone it is
  larger because post-menopausal bone-density loss is steeper.

:func:`tolerance_factor` turns this into a multiplier on the onset. Each
injury carries a tissue class; bone scales strongly with age and moderately
with sex, cartilage and joint/ligament moderately, and muscle, soft tissue,
viscera and neural/vascular tissue weakly. A factor below one means a lower
tolerance - the injury is reached at a lower load - and shifts the
probability band toward "certain"; a factor above one shifts it toward
"impossible". With sex unspecified and no age supplied the factor is one
and the table is the mixed-cadaver baseline. Full citations are in
``docs/biomechanics-sources.md``.

:func:`injury_table` returns the reference table. :func:`predict_injuries`
positions a set of input numbers against it, optionally for a given sex
and age.
"""

from __future__ import annotations

from dataclasses import dataclass

PROBABILITY_BANDS = (
    "certain",
    "highly probable",
    "moderately probable",
    "low probability",
    "impossible",
)

POSTERIOR_CHEST_WALL = "posterior chest wall"
THORACIC_SPINE = "thoracic spine"
THORACIC_VISCERA = "thoracic viscera"
SHOULDER_GIRDLE = "shoulder girdle"
CERVICAL_SPINE = "cervical spine"

# Tissue classes - the demographic sensitivity of an injury is set by the
# tissue that fails, not by the body region it sits in.
TISSUE_CLASSES = (
    "bone",
    "cartilage",
    "joint/ligament",
    "muscle",
    "soft tissue",
    "viscera",
    "neural/vascular",
)

# Standard-adult reference age - the young-adult bone-strength plateau is
# 25-40 yr; 35 yr is taken as the mixed-cadaver baseline. ``age=None`` in
# the predictor means "assume a standard adult" and resolves to this value.
REFERENCE_AGE = 35.0

# Per-tissue demographic sensitivity: (age_slope, sex_gap).
#   age_slope - fractional loss of tolerance per year of age above the
#               reference; 0.011/yr for bone gives a ~44% loss from 35 to
#               75 yr, matching the rib-fracture-risk-with-age literature.
#   sex_gap   - total male-female spread in tolerance; the male tolerance is
#               +sex_gap/2 and the female -sex_gap/2 about the mixed
#               baseline. The bone gap is geometric (rib thickness and
#               cross-section), not material.
_TISSUE_DEMOGRAPHICS: dict[str, tuple[float, float]] = {
    "bone": (0.011, 0.20),
    "cartilage": (0.006, 0.10),
    "joint/ligament": (0.004, 0.08),
    "muscle": (0.003, 0.06),
    "soft tissue": (0.003, 0.04),
    "viscera": (0.0015, 0.02),
    "neural/vascular": (0.003, 0.03),
}

# the age multiplier is clamped to a sane band so extreme ages do not drive
# the onset to zero or to an implausibly high value
_AGE_FACTOR_FLOOR = 0.40
_AGE_FACTOR_CEIL = 1.20


@dataclass(frozen=True)
class InjuryThreshold:
    """One injury, its key-indicator threshold and its scenario probability."""

    injury: str
    region: str
    tissue: str  # tissue class that fails - sets the demographic sensitivity
    ais: int  # Abbreviated Injury Scale severity, 1 (minor) to 6 (maximal)
    metric: str  # key indicator: "energy", "force" or "pressure"
    onset: float  # value of the key indicator at which the injury becomes likely
    unit: str  # "J", "N" or "Pa"
    probability: str  # band for the corridor back-impact scenario, standard adult
    description: str  # why the injury sits in that band
    source: str  # cited source for the injury and its threshold


@dataclass(frozen=True)
class InjuryPrediction:
    """One injury positioned against a supplied input metric.

    When a sex or age is supplied to :func:`predict_injuries` the onset is
    scaled by :func:`tolerance_factor`. ``onset`` is the baseline literature
    threshold; ``adjusted_onset`` is the demographic-scaled threshold the
    input is actually weighed against; ``ratio`` uses the adjusted onset.
    ``probability`` is the band for the supplied demographic and
    ``baseline_probability`` the band for a standard adult.
    """

    injury: str
    region: str
    tissue: str
    ais: int
    metric: str
    value: float  # the supplied input
    onset: float  # the baseline (standard-adult) threshold
    adjusted_onset: float  # the threshold scaled for the supplied sex and age
    unit: str
    ratio: float  # value / adjusted_onset
    probability: str  # band for the supplied demographic
    baseline_probability: str  # band for a standard adult
    tolerance_factor: float  # adjusted_onset / onset
    description: str
    source: str


# Reference table - back-first blunt impact to the posterior thorax. Thirty
# injuries ordered by probability band, each carrying a tissue class, keyed
# off the indicator that governs it (energy, force or pressure) and citing a
# source.
INJURY_TABLE: tuple[InjuryThreshold, ...] = (
    # --- certain ---------------------------------------------------------
    InjuryThreshold(
        "skin and soft-tissue contusion (bruise)",
        POSTERIOR_CHEST_WALL,
        "soft tissue",
        1,
        "pressure",
        50_000.0,
        "Pa",
        "certain",
        "Contact pressure of 80-320 kPa over the posterior-thorax patch is "
        "several times the ~50 kPa at which surface capillaries rupture; a "
        "bruise cannot be avoided.",
        "StatPearls, Blunt Force Trauma (NBK470338); Pathology Outlines, blunt-force injuries",
    ),
    InjuryThreshold(
        "deep paraspinal muscle contusion",
        POSTERIOR_CHEST_WALL,
        "muscle",
        1,
        "force",
        1700.0,
        "N",
        "certain",
        "Contact force of 2.4-6.4 kN across the impact-model range exceeds the "
        "~1.7 kN threshold for measurable deep-muscle oedema even at the low end.",
        "experimental human muscle contusion (PMC9671306)",
    ),
    # --- highly probable -------------------------------------------------
    InjuryThreshold(
        "skin abrasion",
        POSTERIOR_CHEST_WALL,
        "soft tissue",
        1,
        "pressure",
        60_000.0,
        "Pa",
        "highly probable",
        "Friction as the back loads and slides against the door abrades the "
        "epidermis once contact pressure is established; abrasion needs some "
        "tangential motion, so it is highly rather than fully certain.",
        "StatPearls, Blunt Force Trauma (NBK470338); Trauma Forensics in Blunt "
        "and Sharp Force Injuries (PMC9802595)",
    ),
    InjuryThreshold(
        "posterior soft-tissue haematoma",
        POSTERIOR_CHEST_WALL,
        "soft tissue",
        1,
        "pressure",
        90_000.0,
        "Pa",
        "highly probable",
        "A blood collection within the posterior muscle depends on how "
        "concentrated the contact is; at the 80-320 kPa pressure band it is "
        "highly probable.",
        "StatPearls, haematoma (NBK519551); delayed chest-wall haematoma (PMC9066913)",
    ),
    InjuryThreshold(
        "scapular contusion (periosteal bruising)",
        SHOULDER_GIRDLE,
        "soft tissue",
        1,
        "pressure",
        80_000.0,
        "Pa",
        "highly probable",
        "The contact patch falls on the scapular region; periosteal and muscle "
        "bruising follows directly from the contact pressure there.",
        "scapular fractures in blunt chest trauma (PMC5175523); StatPearls, "
        "scapula anatomy (NBK538319)",
    ),
    InjuryThreshold(
        "posterior rib fracture (single)",
        POSTERIOR_CHEST_WALL,
        "bone",
        2,
        "energy",
        60.0,
        "J",
        "highly probable",
        "Delivered energy is 3-4 times the ~60 J above which rib fracture "
        "appears in most cadaver thoracic-impact tests; the posterior arc is "
        "the rib's weakest point in bending.",
        "rib fracture and pulmonary injury thresholds (PMC10121455); Kroell, "
        "Schneider & Nahum 1971, 15th Stapp",
    ),
    InjuryThreshold(
        "costovertebral / costotransverse joint sprain",
        THORACIC_SPINE,
        "joint/ligament",
        1,
        "force",
        1500.0,
        "N",
        "highly probable",
        "The costovertebral and costotransverse joints take the posterior load "
        "directly and sprain well below the rib-fracture force.",
        "traumatic costovertebral joint injury (PMC7437871)",
    ),
    InjuryThreshold(
        "intercostal muscle tear",
        POSTERIOR_CHEST_WALL,
        "muscle",
        2,
        "force",
        2200.0,
        "N",
        "highly probable",
        "Stretch of the intercostal muscle as the rib cage deflects tears "
        "fibres once the contact force passes ~2.2 kN, reached across most of "
        "the impact range.",
        "athletic injuries of the thoracic cage (RadioGraphics); intercostal "
        "muscle strain (Physiopedia)",
    ),
    InjuryThreshold(
        "costochondral separation",
        POSTERIOR_CHEST_WALL,
        "cartilage",
        2,
        "force",
        2500.0,
        "N",
        "highly probable",
        "The rib-to-cartilage junction is a stress concentration; separation "
        "is a common blunt-chest-trauma finding within this impact's force range.",
        "costal cartilage injuries in blunt chest trauma (RSNA Radiology, 2017)",
    ),
    InjuryThreshold(
        "cervical hyperextension / whiplash",
        CERVICAL_SPINE,
        "joint/ligament",
        1,
        "energy",
        40.0,
        "J",
        "highly probable",
        "The trunk stops abruptly against the door while the head, carrying "
        "its own inertia, extends backward on the neck - a cervical "
        "hyperextension sprain that needs only a modest impact.",
        "StatPearls, cervical sprain (NBK541016)",
    ),
    # --- moderately probable --------------------------------------------
    InjuryThreshold(
        "multiple rib fracture (two or more)",
        POSTERIOR_CHEST_WALL,
        "bone",
        3,
        "force",
        3400.0,
        "N",
        "moderately probable",
        "Cadaver thoracic loads above ~3.4 kN drive multiple-rib fracture; the "
        "impact's 2.4-6.4 kN peak straddles that threshold, so the outcome "
        "turns on the contact stiffness.",
        "Kroell, Schneider & Nahum 1971, 15th Stapp; Viano 1989, 33rd Stapp",
    ),
    InjuryThreshold(
        "thoracic spinous / transverse process fracture",
        THORACIC_SPINE,
        "bone",
        2,
        "force",
        3000.0,
        "N",
        "moderately probable",
        "The spinous and transverse processes are posterior elements struck "
        "directly by a flat wall; they fracture at lower force than the "
        "vertebral body.",
        "isolated thoracic and lumbar transverse-process fractures (PMC10407537)",
    ),
    InjuryThreshold(
        "upper thoracic vertebral compression fracture (T1-T8)",
        THORACIC_SPINE,
        "bone",
        2,
        "force",
        3400.0,
        "N",
        "moderately probable",
        "Thoracolumbar impact biomechanics give a 50% T1-T8 fracture "
        "probability at 3.4 kN, inside the impact's force range.",
        "biomechanics of thoracolumbar trauma (PMC3861829)",
    ),
    InjuryThreshold(
        "pulmonary contusion",
        THORACIC_VISCERA,
        "viscera",
        3,
        "force",
        3400.0,
        "N",
        "moderately probable",
        "A fractured or sharply deflected rib bruises the underlying lung; "
        "pulmonary contusion tracks the multiple-rib-fracture threshold.",
        "rib fracture and pulmonary injury thresholds (PMC10121455)",
    ),
    InjuryThreshold(
        "thoracic intervertebral disc injury",
        THORACIC_SPINE,
        "cartilage",
        2,
        "force",
        3800.0,
        "N",
        "moderately probable",
        "The thoracic discs are stiffer and better splinted by the rib cage "
        "than lumbar discs; injury needs force toward the middle of the range.",
        "StatPearls, disc herniation (NBK441822)",
    ),
    InjuryThreshold(
        "thoracic interspinous / supraspinous ligament rupture",
        THORACIC_SPINE,
        "joint/ligament",
        2,
        "force",
        3500.0,
        "N",
        "moderately probable",
        "The posterior ligamentous complex is loaded in tension as the spine "
        "extends over the contact; rupture is possible within the force range.",
        "Benedetti et al. 2000, MR imaging of spinal ligamentous injury (AJR)",
    ),
    InjuryThreshold(
        "thoracic facet (zygapophyseal) joint injury",
        THORACIC_SPINE,
        "joint/ligament",
        2,
        "force",
        3200.0,
        "N",
        "moderately probable",
        "The thoracic facet joints carry part of the posterior load; capsule "
        "and cartilage injury occurs near the middle of the impact range.",
        "spinal facet joint biomechanics (PMC3705911)",
    ),
    InjuryThreshold(
        "lung laceration",
        THORACIC_VISCERA,
        "viscera",
        4,
        "force",
        4000.0,
        "N",
        "moderately probable",
        "A sharply deflected or fractured rib can shear the lung surface; "
        "laceration is downstream of rib fracture and shares its force range.",
        "blunt chest wall and pulmonary injuries (PMC7296362)",
    ),
    # --- low probability -------------------------------------------------
    InjuryThreshold(
        "flail chest (three or more consecutive ribs)",
        POSTERIOR_CHEST_WALL,
        "bone",
        4,
        "force",
        5500.0,
        "N",
        "low probability",
        "A flail segment needs three or more consecutive ribs each broken in "
        "two places, requiring force at or beyond the top of this impact's range.",
        "StatPearls, flail chest (NBK534090)",
    ),
    InjuryThreshold(
        "pneumothorax / haemothorax",
        THORACIC_VISCERA,
        "viscera",
        3,
        "force",
        4500.0,
        "N",
        "low probability",
        "Air or blood in the pleural space needs a displaced rib end to breach "
        "the pleura; a single non-displaced fracture rarely does.",
        "StatPearls, pneumothorax (NBK441885)",
    ),
    InjuryThreshold(
        "thoracic vertebral burst fracture",
        THORACIC_SPINE,
        "bone",
        3,
        "force",
        6000.0,
        "N",
        "low probability",
        "A burst pattern needs high axial compression; a back-first impact "
        "loads the spine mainly in extension, so the burst mechanism is "
        "unlikely here.",
        "biomechanics of thoracolumbar burst fractures (PMC4111950)",
    ),
    InjuryThreshold(
        "spinal cord injury / neurological deficit",
        THORACIC_SPINE,
        "neural/vascular",
        4,
        "force",
        6500.0,
        "N",
        "low probability",
        "Cord injury follows an unstable vertebral fracture or dislocation and "
        "is downstream of the low-probability burst and dislocation patterns.",
        "StatPearls, traumatic spinal cord injury (NBK560721)",
    ),
    InjuryThreshold(
        "costovertebral joint dislocation",
        THORACIC_SPINE,
        "joint/ligament",
        2,
        "force",
        5000.0,
        "N",
        "low probability",
        "Frank dislocation of the rib-spine joint needs force beyond the sprain "
        "range, toward the upper end of this impact.",
        "traumatic costovertebral joint dislocation (PMC7437871)",
    ),
    InjuryThreshold(
        "cardiac contusion",
        THORACIC_VISCERA,
        "viscera",
        3,
        "force",
        6000.0,
        "N",
        "low probability",
        "The heart is an anterior structure; a posterior impact transmits load "
        "to it poorly, and cardiac contusion is normally a frontal-impact injury.",
        "StatPearls, blunt cardiac injury (NBK532267)",
    ),
    InjuryThreshold(
        "trapezius / rhomboid muscle tear",
        POSTERIOR_CHEST_WALL,
        "muscle",
        2,
        "force",
        5000.0,
        "N",
        "low probability",
        "A frank tear of the scapular-stabiliser muscles is an uncommon "
        "isolated blunt-impact injury, needing force toward the upper end of "
        "this impact.",
        "lower trapezius muscle avulsion (PMC4899989)",
    ),
    InjuryThreshold(
        "subscapular haematoma",
        SHOULDER_GIRDLE,
        "soft tissue",
        2,
        "force",
        5000.0,
        "N",
        "low probability",
        "A blood collection between the scapula and chest wall is a rare "
        "blunt-trauma finding, needing force toward the upper end of this impact.",
        "delayed dorsal scapular artery haematoma (PMC9066913)",
    ),
    InjuryThreshold(
        "spinal epidural haematoma",
        THORACIC_SPINE,
        "neural/vascular",
        3,
        "force",
        6000.0,
        "N",
        "low probability",
        "Bleeding into the spinal epidural space is a rare blunt-trauma injury; "
        "it needs force at the top of this impact's range and usually a "
        "hyperflexion component.",
        "StatPearls, spinal epidural haematoma (NBK518982)",
    ),
    # --- impossible ------------------------------------------------------
    InjuryThreshold(
        "scapular fracture",
        SHOULDER_GIRDLE,
        "bone",
        2,
        "force",
        15000.0,
        "N",
        "impossible",
        "The scapula is buffered by 3-4 cm of muscle and fractures only under "
        "motor-vehicle-level energy; the ~15 kN threshold is far above the "
        "2.4-6.4 kN this impact delivers.",
        "StatPearls, scapula fracture (NBK537312); scapular fractures in blunt "
        "chest trauma (PMC5175523)",
    ),
    InjuryThreshold(
        "aortic rupture or transection",
        THORACIC_VISCERA,
        "neural/vascular",
        5,
        "energy",
        5000.0,
        "J",
        "impossible",
        "Aortic disruption is a high-deceleration injury of motor-vehicle "
        "crashes and falls from height; the energy needed is more than an "
        "order of magnitude above this impact's 194-262 J.",
        "blunt thoracic aortic injury, review (Springer)",
    ),
    InjuryThreshold(
        "thoracic fracture-dislocation (unstable spine)",
        THORACIC_SPINE,
        "bone",
        4,
        "force",
        12000.0,
        "N",
        "impossible",
        "An unstable fracture-dislocation of the thoracic spine needs extreme "
        "combined bending and shear far beyond the load this impact develops.",
        "traumatic thoracolumbar spine injuries, review (RadioGraphics)",
    ),
)


def tolerance_factor(
    tissue: str, gender: str = "unspecified", age: float | None = None
) -> float:
    """Demographic multiplier on an injury onset for a given sex and age.

    The onset thresholds in :data:`INJURY_TABLE` are a mixed-cadaver
    baseline - a standard adult (``REFERENCE_AGE``), sex unspecified. This
    function returns the factor by which that onset is scaled for a
    particular subject. A factor below one means a lower tolerance: the
    injury is reached at a lower load.

    The factor is the product of an age component and a sex component, both
    set by the tissue class:

    - **age** - tolerance falls by ``age_slope`` per year above the
      reference. The slope is steep for bone (1.1%/yr - rib cortical bone
      loses roughly 12% of its failure strain per decade, so tolerance
      roughly halves from 35 to 75 yr), moderate for cartilage and
      joint/ligament, and slight for muscle, soft tissue, viscera and
      neural/vascular tissue. The age component is clamped to
      ``[0.40, 1.20]``.
    - **sex** - the male tolerance is ``+sex_gap/2`` and the female
      ``-sex_gap/2`` about the baseline. The bone gap (20%) is geometric -
      female ribs are thinner and smaller in cross-section, not weaker in
      material. Other tissues carry a smaller gap.

    ``gender`` accepts ``"male"``, ``"female"`` or ``"unspecified"`` (also
    ``"m"`` / ``"f"``). ``age`` is in years; ``None`` means a standard adult
    and resolves to ``REFERENCE_AGE``. With sex unspecified and no age the
    factor is exactly ``1.0``.
    """
    if tissue not in _TISSUE_DEMOGRAPHICS:
        raise ValueError(f"unknown tissue class: {tissue!r}")
    age_slope, sex_gap = _TISSUE_DEMOGRAPHICS[tissue]

    subject_age = REFERENCE_AGE if age is None else float(age)
    age_part = 1.0 - age_slope * (subject_age - REFERENCE_AGE)
    age_part = min(_AGE_FACTOR_CEIL, max(_AGE_FACTOR_FLOOR, age_part))

    g = gender.strip().lower()
    if g in ("male", "m"):
        sex_part = 1.0 + sex_gap / 2.0
    elif g in ("female", "f"):
        sex_part = 1.0 - sex_gap / 2.0
    elif g in ("unspecified", "unknown", ""):
        sex_part = 1.0
    else:
        raise ValueError(
            f"gender must be 'male', 'female' or 'unspecified', got {gender!r}"
        )
    return age_part * sex_part


def _shift_band(baseline: str, factor: float) -> str:
    """Shift a probability band by the demographic tolerance factor.

    A lower tolerance (factor below one) moves the band toward "certain"; a
    higher tolerance moves it toward "impossible". The shift is in whole
    bands so the curated standard-adult judgement is preserved as the
    starting point.
    """
    idx = PROBABILITY_BANDS.index(baseline)
    if factor <= 0.65:
        idx -= 2
    elif factor <= 0.85:
        idx -= 1
    elif factor >= 1.18:
        idx += 1
    idx = min(len(PROBABILITY_BANDS) - 1, max(0, idx))
    return PROBABILITY_BANDS[idx]


def injury_table(
    region: str | None = None, probability: str | None = None
) -> list[InjuryThreshold]:
    """The injury reference table, optionally filtered by region or band."""
    rows = list(INJURY_TABLE)
    if region is not None:
        rows = [r for r in rows if r.region == region]
    if probability is not None:
        rows = [r for r in rows if r.probability == probability]
    return rows


def predict_injuries(
    metrics: dict[str, float],
    region: str | None = None,
    gender: str = "unspecified",
    age: float | None = None,
) -> list[InjuryPrediction]:
    """Position a set of input metrics against the injury reference table.

    ``metrics`` is a dictionary of input numbers keyed by metric name -
    e.g. ``{"energy": 262.0, "force": 6400.0, "pressure": 200000.0}``. Every
    table row (optionally filtered to ``region``) whose metric is present in
    ``metrics`` is returned with the ratio of the input to the onset
    threshold.

    ``gender`` and ``age`` set the subject the table is read for.
    :func:`tolerance_factor` scales each row's onset for the subject's
    tissue class: ``adjusted_onset`` is the scaled threshold, ``ratio`` is
    the input over it, and ``probability`` is the band shifted from the
    standard-adult ``baseline_probability``. ``age`` defaults to a standard
    adult when not supplied; with ``gender="unspecified"`` and no ``age``
    the factor is one and the prediction is the mixed-cadaver baseline.
    Metric keys with no matching row are ignored.
    """
    out = []
    for row in INJURY_TABLE:
        if region is not None and row.region != region:
            continue
        if row.metric not in metrics:
            continue
        value = float(metrics[row.metric])
        factor = tolerance_factor(row.tissue, gender, age)
        adjusted_onset = row.onset * factor
        ratio = value / adjusted_onset if adjusted_onset > 0 else 0.0
        out.append(
            InjuryPrediction(
                injury=row.injury,
                region=row.region,
                tissue=row.tissue,
                ais=row.ais,
                metric=row.metric,
                value=value,
                onset=row.onset,
                adjusted_onset=adjusted_onset,
                unit=row.unit,
                ratio=ratio,
                probability=_shift_band(row.probability, factor),
                baseline_probability=row.probability,
                tolerance_factor=factor,
                description=row.description,
                source=row.source,
            )
        )
    return out


__all__ = [
    "CERVICAL_SPINE",
    "INJURY_TABLE",
    "POSTERIOR_CHEST_WALL",
    "PROBABILITY_BANDS",
    "REFERENCE_AGE",
    "SHOULDER_GIRDLE",
    "THORACIC_SPINE",
    "THORACIC_VISCERA",
    "TISSUE_CLASSES",
    "InjuryPrediction",
    "InjuryThreshold",
    "injury_table",
    "predict_injuries",
    "tolerance_factor",
]
