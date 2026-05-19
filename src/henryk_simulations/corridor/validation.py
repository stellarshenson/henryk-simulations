"""Physical validation of the merged simulation configuration.

``simconfig.py`` calls :func:`validate` on the merged parameter set at
import. A value outside its physical-plausibility range, a non-finite
value, or a broken cross-parameter invariant raises
:class:`ConfigValidationError` - the config fails loud before any
simulation runs.
"""

from __future__ import annotations

import math
from typing import Any


class ConfigValidationError(ValueError):
    """A simulation_config parameter is physically implausible."""


# (section, key) -> (low, high) inclusive physical-plausibility range.
# A value outside the range, or non-finite, is a hard error.
BOUNDS: dict[tuple[str, str], tuple[float, float]] = {
    ("body", "body_mass"): (20.0, 300.0),
    ("body", "body_height"): (0.5, 2.5),
    ("body", "yaw_inertia_per_kg"): (0.001, 0.2),
    ("body", "m_eff_fraction"): (0.0, 1.0),
    ("body", "m_skin_fraction"): (0.0, 1.0),
    ("body", "m_scapula_fraction"): (0.0, 1.0),
    ("body", "m_ribcage_fraction"): (0.0, 1.0),
    ("body", "m_organ_fraction"): (0.0, 1.0),
    ("body", "m_spine_fraction"): (0.0, 1.0),
    ("acoustics", "v_close"): (0.0, 20.0),
    ("acoustics", "mic_distance"): (0.01, 1000.0),
    ("acoustics", "air_rho"): (0.5, 2.0),
    ("acoustics", "air_c"): (300.0, 360.0),
    ("acoustics", "sample_rate"): (8000.0, 192000.0),
    ("choreography", "phase1_duration"): (0.01, 60.0),
    ("choreography", "phase2_duration"): (0.01, 60.0),
    ("choreography", "arc_length"): (0.0, 50.0),
    ("choreography", "lateral_offset"): (0.0, 10.0),
    ("choreography", "return_translation"): (0.0, 50.0),
    ("choreography", "rotation"): (0.0, 4.0 * math.pi),
    ("choreography", "body_compression"): (0.001, 0.3),
    ("choreography", "body_compression_min"): (0.001, 0.3),
    ("choreography", "body_compression_max"): (0.001, 0.3),
    ("choreography", "body_thickness"): (0.05, 1.0),
    ("choreography", "t_give"): (0.001, 5.0),
    ("choreography", "t_letgo"): (0.001, 5.0),
    ("choreography", "ramp_min"): (0.001, 5.0),
    ("choreography", "ramp_max"): (0.001, 5.0),
    ("choreography", "a_max_ceiling"): (0.1, 50.0),
    ("choreography", "a_max_typical"): (0.1, 50.0),
    ("choreography", "jerk_ceiling"): (1.0, 1000.0),
    ("impact", "subject_age"): (0.0, 130.0),
    ("impact", "k_skin"): (1e3, 1e10),
    ("impact", "k_scapula"): (1e3, 1e10),
    ("impact", "k_rib"): (1e3, 1e10),
    ("impact", "k_spine"): (1e3, 1e10),
    ("impact", "c_skin"): (0.0, 1e6),
    ("impact", "c_scapula"): (0.0, 1e6),
    ("impact", "c_rib"): (0.0, 1e6),
    ("impact", "c_spine"): (0.0, 1e6),
    ("impact", "k_contact"): (1e3, 1e10),
    ("impact", "n_contact"): (1.0, 3.0),
    ("impact", "lambda_hc"): (0.0, 100.0),
    ("impact", "yield_force"): (100.0, 1e6),
    ("impact", "area_initial"): (1e-4, 1.0),
    ("impact", "area_final"): (1e-4, 1.0),
    ("impact", "area_tau"): (1e-4, 1.0),
    ("impact", "n_ribs_span"): (1.0, 24.0),
    ("bodyfem", "torso_z_lo_frac"): (0.0, 1.0),
    ("bodyfem", "torso_z_hi_frac"): (0.0, 1.0),
    ("bodyfem", "torso_x_halfwidth"): (0.01, 1.0),
    ("bodyfem", "restitution"): (0.0, 1.0),
    ("bodyfem", "contact_time"): (0.001, 1.0),
    ("bodyfem", "youngs_modulus"): (1e3, 1e9),
    ("bodyfem", "poisson"): (0.0, 0.5),
    ("bodyfem", "density"): (1.0, 30000.0),
    ("bodyfem", "modal_damping"): (0.0, 1.0),
    ("bodyfem", "contact_patch_area"): (1e-4, 1.0),
    ("bodyfem", "gap_squeeze_start"): (1e-4, 0.1),
    ("bodyfem", "gap_seal"): (1e-4, 0.1),
    ("bodyfem", "escape_band_lo"): (1.0, 22050.0),
    ("bodyfem", "escape_band_hi"): (1.0, 22050.0),
    ("bodyfem", "surface_roughness"): (0.0, 2.0),
    ("doorfem", "panel_width"): (0.1, 10.0),
    ("doorfem", "panel_height"): (0.1, 10.0),
    ("doorfem", "skin_thickness"): (1e-4, 0.1),
    ("doorfem", "cavity_gap"): (0.001, 1.0),
    ("doorfem", "frame_width"): (0.001, 1.0),
    ("doorfem", "window_width"): (0.0, 10.0),
    ("doorfem", "window_height"): (0.0, 10.0),
    ("doorfem", "window_cx"): (0.0, 10.0),
    ("doorfem", "window_cy"): (0.0, 10.0),
    ("doorfem", "youngs_modulus"): (1e9, 1e12),
    ("doorfem", "poisson"): (0.0, 0.5),
    ("doorfem", "density"): (1.0, 30000.0),
    ("doorfem", "modal_damping"): (0.0, 1.0),
    ("doorfem", "strike_x"): (0.0, 10.0),
    ("doorfem", "strike_y"): (0.0, 10.0),
    ("reverb", "corridor_width"): (0.1, 1000.0),
    ("reverb", "corridor_length"): (0.1, 1000.0),
    ("reverb", "source_x"): (0.0, 1000.0),
    ("reverb", "source_y"): (0.0, 1000.0),
    ("reverb", "mic_x"): (0.0, 1000.0),
    ("reverb", "mic_y"): (0.0, 1000.0),
    ("reverb", "wall_reflection"): (0.0, 1.0),
    ("audiomix", "peak_time"): (0.0, 1e4),
    ("audiomix", "toy_release_time"): (0.0, 1e4),
    ("audiomix", "scream_time"): (0.0, 1e4),
    ("audiomix", "thump_gain"): (0.0, 1e3),
    ("audiomix", "clang_gain"): (0.0, 1e3),
    ("audiomix", "headroom"): (0.0, 1.0),
}

# the 5-DOF posterior-thorax chain mass fractions, which must sum to 1.0
CHAIN_FRACTION_KEYS = (
    "m_skin_fraction",
    "m_scapula_fraction",
    "m_ribcage_fraction",
    "m_organ_fraction",
    "m_spine_fraction",
)


def _require(ok: bool, message: str) -> None:
    """Raise ConfigValidationError with ``message`` unless ``ok``."""
    if not ok:
        raise ConfigValidationError(message)


def validate(params: dict[str, dict[str, Any]]) -> None:
    """Validate the merged simulation config; raise on the first violation."""
    # per-parameter physical bounds
    for (section, key), (low, high) in BOUNDS.items():
        if section not in params or key not in params[section]:
            continue
        value = params[section][key]
        if value is None:
            continue  # an optional parameter left unset (e.g. subject_age)
        if not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ConfigValidationError(f"{section}.{key} must be a finite number, got {value!r}")
        if not low <= value <= high:
            raise ConfigValidationError(
                f"{section}.{key} = {value} is outside the physical range [{low}, {high}]"
            )

    # subject sex must be one of the two recognised codes
    gender = params.get("impact", {}).get("subject_gender")
    _require(
        gender in ("F", "M"),
        f"impact.subject_gender must be 'F' or 'M', got {gender!r}",
    )

    # cross-parameter invariants
    cho = params["choreography"]
    _require(
        cho["body_compression_min"] <= cho["body_compression"] <= cho["body_compression_max"],
        "choreography: body_compression must lie within "
        "[body_compression_min, body_compression_max]",
    )
    _require(
        cho["ramp_min"] <= cho["ramp_max"],
        "choreography: ramp_min must not exceed ramp_max",
    )
    for ramp in ("t_give", "t_letgo"):
        _require(
            cho["ramp_min"] <= cho[ramp] <= cho["ramp_max"],
            f"choreography.{ramp} must lie within the RFD ramp band [ramp_min, ramp_max]",
        )
    _require(
        cho["a_max_typical"] <= cho["a_max_ceiling"],
        "choreography: a_max_typical must not exceed a_max_ceiling",
    )

    bodyfem = params["bodyfem"]
    _require(
        bodyfem["escape_band_lo"] < bodyfem["escape_band_hi"],
        "bodyfem: escape_band_lo must be below escape_band_hi",
    )
    _require(
        bodyfem["torso_z_lo_frac"] < bodyfem["torso_z_hi_frac"],
        "bodyfem: torso_z_lo_frac must be below torso_z_hi_frac",
    )
    _require(
        bodyfem["gap_seal"] < bodyfem["gap_squeeze_start"],
        "bodyfem: gap_seal must be below gap_squeeze_start",
    )

    impact = params["impact"]
    _require(
        impact["area_initial"] <= impact["area_final"],
        "impact: area_initial must not exceed area_final",
    )

    # the 5-DOF chain mass fractions must sum to 1.0
    body = params["body"]
    total = sum(body[key] for key in CHAIN_FRACTION_KEYS)
    _require(
        abs(total - 1.0) < 1e-6,
        f"body: the 5-DOF chain mass fractions must sum to 1.0, got {total}",
    )


__all__ = ["BOUNDS", "CHAIN_FRACTION_KEYS", "ConfigValidationError", "validate"]
