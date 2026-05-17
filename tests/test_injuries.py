"""Guards for the injury reference table and predictor."""

from __future__ import annotations

import pytest

from henryk_simulations.corridor import (
    INJURY_TABLE,
    InjuryPrediction,
    InjuryThreshold,
    injury_table,
    predict_injuries,
)
from henryk_simulations.corridor.injuries import POSTERIOR_CHEST_WALL, PROBABILITY_BANDS


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
