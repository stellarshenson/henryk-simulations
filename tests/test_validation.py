"""Tests for the physical validation of the simulation configuration.

`validation.validate` runs on the merged config at import. These guards
confirm the shipped config passes, and that every physical bound and
cross-parameter invariant actually fires on a bad value.
"""

from __future__ import annotations

import copy
import math

import pytest

from henryk_simulations.corridor import simconfig
from henryk_simulations.corridor.impact import DE_LEVA_MALE
from henryk_simulations.corridor.validation import (
    BOUNDS,
    ConfigValidationError,
    validate,
)


def _good() -> dict:
    """A fresh, mutable copy of the merged, valid simulation config."""
    return copy.deepcopy(simconfig._PARAMS)


def test_shipped_config_validates_clean() -> None:
    """The library defaults + user file pass validation as shipped."""
    validate(_good())


@pytest.mark.parametrize(("section", "key"), sorted(BOUNDS))
def test_each_bound_fires(section: str, key: str) -> None:
    """A value just past either edge of every BOUNDS range is rejected."""
    low, high = BOUNDS[(section, key)]
    for bad in (low - 1.0, high + 1.0):
        config = _good()
        config[section][key] = bad
        with pytest.raises(ConfigValidationError):
            validate(config)


def test_non_finite_value_is_rejected() -> None:
    config = _good()
    config["body"]["body_mass"] = math.inf
    with pytest.raises(ConfigValidationError):
        validate(config)


def test_negative_stiffness_is_rejected() -> None:
    config = _good()
    config["impact"]["k_skin"] = -5.0
    with pytest.raises(ConfigValidationError):
        validate(config)


def test_unphysical_poisson_is_rejected() -> None:
    config = _good()
    config["bodyfem"]["poisson"] = 0.7  # exceeds the 0.5 isotropic limit
    with pytest.raises(ConfigValidationError):
        validate(config)


def test_unknown_subject_gender_is_rejected() -> None:
    config = _good()
    config["impact"]["subject_gender"] = "X"
    with pytest.raises(ConfigValidationError):
        validate(config)


def test_compression_order_invariant_fires() -> None:
    config = _good()
    cho = config["choreography"]
    cho["body_compression"] = cho["body_compression_max"] + 0.01
    with pytest.raises(ConfigValidationError):
        validate(config)


def test_ramp_band_invariant_fires() -> None:
    config = _good()
    cho = config["choreography"]
    cho["t_give"] = cho["ramp_max"] + 0.01
    with pytest.raises(ConfigValidationError):
        validate(config)


def test_escape_band_invariant_fires() -> None:
    config = _good()
    bodyfem = config["bodyfem"]
    bodyfem["escape_band_lo"] = bodyfem["escape_band_hi"] + 1.0
    with pytest.raises(ConfigValidationError):
        validate(config)


def test_area_order_invariant_fires() -> None:
    config = _good()
    impact = config["impact"]
    impact["area_initial"] = impact["area_final"] + 0.001
    with pytest.raises(ConfigValidationError):
        validate(config)


def test_gap_order_invariant_fires() -> None:
    config = _good()
    bodyfem = config["bodyfem"]
    bodyfem["gap_seal"] = bodyfem["gap_squeeze_start"] + 0.001
    with pytest.raises(ConfigValidationError):
        validate(config)


def test_chain_fractions_must_sum_to_one() -> None:
    config = _good()
    config["body"]["m_skin_fraction"] = 0.5  # breaks the sum-to-1 invariant
    with pytest.raises(ConfigValidationError):
        validate(config)


def test_de_leva_segment_fractions_sum_to_one() -> None:
    """The de Leva segment table (source reference data) is self-consistent."""
    total = sum(count * fraction for _, count, fraction in DE_LEVA_MALE.values())
    assert total == pytest.approx(1.0)
