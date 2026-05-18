"""Guards for the injury reference table and predictor."""

from __future__ import annotations

import pytest

from henryk_simulations.corridor import (
    INJURY_TABLE,
    InjuryPrediction,
    InjuryThreshold,
    injury_table,
    predict_injuries,
    tolerance_factor,
)
from henryk_simulations.corridor.injuries import (
    POSTERIOR_CHEST_WALL,
    PROBABILITY_BANDS,
    REFERENCE_AGE,
    TISSUE_CLASSES,
)

# ---------------------------------------------------------------------------
# Reference table
# ---------------------------------------------------------------------------


def test_table_has_about_thirty_rows() -> None:
    assert 28 <= len(INJURY_TABLE) <= 34


def test_table_rows_are_well_formed() -> None:
    for row in INJURY_TABLE:
        assert isinstance(row, InjuryThreshold)
        assert row.injury and row.region
        assert row.metric in ("energy", "force", "pressure")
        assert row.onset > 0.0
        assert row.unit in ("J", "N", "Pa")
        assert 1 <= row.ais <= 6
        assert row.probability in PROBABILITY_BANDS
        assert row.tissue in TISSUE_CLASSES
        assert len(row.description) > 30


def test_every_row_has_a_source() -> None:
    for row in INJURY_TABLE:
        assert row.source and len(row.source) > 10


def test_all_five_probability_bands_are_represented() -> None:
    bands = {row.probability for row in INJURY_TABLE}
    assert bands == set(PROBABILITY_BANDS)


def test_all_three_metrics_are_used() -> None:
    metrics = {row.metric for row in INJURY_TABLE}
    assert metrics == {"energy", "force", "pressure"}


def test_table_covers_contusion_fracture_and_impossible() -> None:
    injuries = {t.injury for t in INJURY_TABLE}
    assert any("contusion" in i for i in injuries)
    assert any("rib fracture" in i for i in injuries)
    assert any(t.probability == "impossible" for t in INJURY_TABLE)


def test_injury_table_filters_by_region() -> None:
    chest = injury_table(region=POSTERIOR_CHEST_WALL)
    assert chest
    assert all(t.region == POSTERIOR_CHEST_WALL for t in chest)


def test_injury_table_filters_by_probability() -> None:
    certain = injury_table(probability="certain")
    assert certain
    assert all(t.probability == "certain" for t in certain)


def test_scapular_fracture_is_impossible() -> None:
    # the literature is emphatic - scapular fracture needs motor-vehicle energy
    scapular = next(t for t in INJURY_TABLE if t.injury == "scapular fracture")
    assert scapular.probability == "impossible"


# ---------------------------------------------------------------------------
# Prediction
# ---------------------------------------------------------------------------


def test_predict_returns_predictions() -> None:
    preds = predict_injuries({"energy": 262.0, "force": 6400.0, "pressure": 200_000.0})
    assert preds
    for p in preds:
        assert isinstance(p, InjuryPrediction)
        assert p.probability in PROBABILITY_BANDS
        assert p.source


def test_ratio_is_value_over_onset() -> None:
    preds = predict_injuries({"energy": 120.0})
    rib = next(p for p in preds if p.injury == "posterior rib fracture (single)")
    assert rib.ratio == pytest.approx(120.0 / 60.0)


def test_delivered_energy_clears_the_rib_fracture_onset() -> None:
    # 262 J of delivered energy is well above the ~60 J rib-fracture threshold
    preds = predict_injuries({"energy": 262.0})
    rib = next(p for p in preds if p.injury == "posterior rib fracture (single)")
    assert rib.ratio > 1.0
    assert rib.probability == "highly probable"


def test_pressure_metric_scores_soft_tissue_rows() -> None:
    preds = predict_injuries({"pressure": 200_000.0})
    assert preds
    assert all(p.metric == "pressure" for p in preds)
    assert any("contusion" in p.injury for p in preds)


def test_metric_only_scored_when_supplied() -> None:
    preds = predict_injuries({"energy": 262.0})
    assert preds
    assert all(p.metric == "energy" for p in preds)


def test_unkeyed_metric_is_ignored() -> None:
    # no table row keys off torque - supplying it must not raise or match
    assert predict_injuries({"torque": 500.0}) == []


def test_region_filter() -> None:
    preds = predict_injuries({"force": 6400.0}, region=POSTERIOR_CHEST_WALL)
    assert preds
    assert all(p.region == POSTERIOR_CHEST_WALL for p in preds)


def test_predictions_carry_description_source_and_ais() -> None:
    for p in predict_injuries({"energy": 262.0, "force": 6400.0, "pressure": 200_000.0}):
        assert len(p.description) > 30
        assert p.source
        assert 1 <= p.ais <= 6


# ---------------------------------------------------------------------------
# Sex and age
# ---------------------------------------------------------------------------


def test_standard_subject_factor_is_one() -> None:
    # sex unspecified, no age - the mixed-cadaver baseline, factor exactly 1
    for tissue in TISSUE_CLASSES:
        assert tolerance_factor(tissue) == pytest.approx(1.0)


def test_reference_age_factor_is_one() -> None:
    assert tolerance_factor("bone", "unspecified", REFERENCE_AGE) == pytest.approx(1.0)


def test_ageing_lowers_bone_tolerance() -> None:
    young = tolerance_factor("bone", "unspecified", 25.0)
    old = tolerance_factor("bone", "unspecified", 75.0)
    assert young > 1.0 > old


def test_bone_is_more_age_sensitive_than_soft_tissue() -> None:
    # bone loses tolerance with age far faster than soft tissue
    bone = tolerance_factor("bone", "unspecified", 80.0)
    soft = tolerance_factor("soft tissue", "unspecified", 80.0)
    assert bone < soft


def test_female_bone_tolerance_below_male() -> None:
    assert tolerance_factor("bone", "female") < tolerance_factor("bone", "male")


def test_gender_aliases_accepted() -> None:
    assert tolerance_factor("bone", "f") == tolerance_factor("bone", "female")
    assert tolerance_factor("bone", "M") == tolerance_factor("bone", "male")


def test_factor_is_clamped_for_extreme_age() -> None:
    assert tolerance_factor("bone", "unspecified", 200.0) == pytest.approx(0.40)


def test_bad_gender_raises() -> None:
    with pytest.raises(ValueError):
        tolerance_factor("bone", "other")


def test_bad_tissue_raises() -> None:
    with pytest.raises(ValueError):
        tolerance_factor("plastic")


def test_predict_default_keeps_baseline_band() -> None:
    # with no demographic supplied the prediction equals the curated baseline
    for p in predict_injuries({"energy": 262.0, "force": 6400.0, "pressure": 200_000.0}):
        assert p.probability == p.baseline_probability
        assert p.tolerance_factor == pytest.approx(1.0)
        assert p.adjusted_onset == pytest.approx(p.onset)


def test_elderly_female_raises_bone_injury_probability() -> None:
    std = next(p for p in predict_injuries({"force": 3400.0})
               if p.injury == "multiple rib fracture (two or more)")
    old = next(p for p in predict_injuries({"force": 3400.0}, gender="female", age=80)
               if p.injury == "multiple rib fracture (two or more)")
    assert old.adjusted_onset < std.adjusted_onset
    assert old.ratio > std.ratio
    bands = list(PROBABILITY_BANDS)
    assert bands.index(old.probability) < bands.index(std.probability)


def test_predictions_carry_tissue_and_demographic_fields() -> None:
    for p in predict_injuries({"force": 6400.0}, gender="female", age=28):
        assert p.tissue in TISSUE_CLASSES
        assert p.adjusted_onset == pytest.approx(p.onset * p.tolerance_factor)
        assert p.baseline_probability in PROBABILITY_BANDS


def test_young_adult_female_keeps_baseline_bands() -> None:
    # a 28-year-old woman sits near the bone-strength peak; the youth bonus
    # and the small geometric sex reduction nearly cancel, so the corridor
    # verdict is unchanged from the standard-adult baseline
    m = {"energy": 262.0, "force": 6400.0, "pressure": 200_000.0}
    base = {p.injury: p.probability for p in predict_injuries(m)}
    for p in predict_injuries(m, gender="female", age=28):
        assert p.probability == base[p.injury]
        assert 0.93 < p.tolerance_factor < 1.02


def test_band_shifts_appear_only_for_older_subjects() -> None:
    # the demographic model leaves a young adult essentially unmoved but
    # shifts bone-injury bands once the subject is elderly
    m = {"energy": 262.0, "force": 6400.0, "pressure": 200_000.0}
    base = predict_injuries(m)
    young = predict_injuries(m, gender="female", age=28)
    elderly = predict_injuries(m, gender="female", age=80)
    moved_young = sum(y.probability != b.probability for y, b in zip(young, base))
    moved_elderly = sum(e.probability != b.probability for e, b in zip(elderly, base))
    assert moved_young == 0
    assert moved_elderly > 0
