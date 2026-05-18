"""Tests for the externalized simulation configuration.

The corridor config dataclasses read their physical/scenario field
defaults from simulation_config.json. These guards keep the JSON and the
dataclasses in lockstep, and check that the physics-linked quantities
(total_time, yaw_inertia, m_eff, the 5-DOF chain) derive correctly rather
than being free parameters that could drift out of sync.
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from henryk_simulations.corridor.audiomix import AudioMixConfig
from henryk_simulations.corridor.bodyfem import BodyFEMConfig
from henryk_simulations.corridor.choreography import ChoreographyConfig
from henryk_simulations.corridor.doorfem import DoorFEMConfig
from henryk_simulations.corridor.impact import ImpactConfig
from henryk_simulations.corridor.reverb import CorridorReverbConfig
from henryk_simulations.corridor.simconfig import CONFIG_PATH, param

# config dataclass keyed by the JSON section it owns
OWN_SECTION = {
    "choreography": ChoreographyConfig,
    "impact": ImpactConfig,
    "bodyfem": BodyFEMConfig,
    "doorfem": DoorFEMConfig,
    "reverb": CorridorReverbConfig,
    "audiomix": AudioMixConfig,
}
# sections read by more than one config - the de-duplicated shared values
SHARED_SECTIONS = ("body", "acoustics")
ALL_SECTIONS = set(OWN_SECTION) | set(SHARED_SECTIONS)


def _json() -> dict:
    """Load simulation_config.json fresh."""
    with open(CONFIG_PATH, encoding="utf-8") as handle:
        return json.load(handle)


def _factory_fields(config_cls: type) -> set[str]:
    """Field names whose default is read from the JSON."""
    return {
        f.name
        for f in dataclasses.fields(config_cls)
        if f.default_factory is not dataclasses.MISSING
    }


def test_config_file_has_expected_sections() -> None:
    assert set(_json()) == ALL_SECTIONS


@pytest.mark.parametrize("section", sorted(OWN_SECTION))
def test_every_field_resolves_to_exactly_one_json_key(section: str) -> None:
    """Each JSON-backed field reads from exactly one section, value matching."""
    data = _json()
    cfg = OWN_SECTION[section]()
    for name in _factory_fields(OWN_SECTION[section]):
        hits = [s for s in (section, *SHARED_SECTIONS) if name in data[s]]
        assert len(hits) == 1, f"{section}.{name} resolves to {hits}"
        assert getattr(cfg, name) == data[hits[0]][name]


def test_no_orphan_json_keys() -> None:
    """Every JSON key is consumed by some config field."""
    consumed: set[str] = set()
    for config_cls in OWN_SECTION.values():
        consumed |= _factory_fields(config_cls)
    for section, keys in _json().items():
        for key in keys:
            assert key in consumed, f"{section}.{key} is unused"


def test_total_time_derives_from_the_phases() -> None:
    cfg = ChoreographyConfig()
    assert cfg.total_time == pytest.approx(cfg.phase1_duration + cfg.phase2_duration)


def test_yaw_inertia_derives_from_body_mass() -> None:
    cfg = ChoreographyConfig()
    assert cfg.yaw_inertia == pytest.approx(cfg.body_mass * cfg.yaw_inertia_per_kg)


def test_m_eff_derives_from_body_mass() -> None:
    cfg = BodyFEMConfig()
    assert cfg.m_eff == pytest.approx(cfg.body_mass * cfg.m_eff_fraction)


def test_chain_masses_scale_and_sum_to_body_mass() -> None:
    cfg = ImpactConfig()
    chain = cfg.m_skin + cfg.m_scapula + cfg.m_ribcage + cfg.m_organ + cfg.m_spine
    assert chain == pytest.approx(cfg.body_mass)


def test_baseline_70kg_values() -> None:
    """The shipped JSON reproduces the canonical 70 kg baseline."""
    choreo = ChoreographyConfig()
    assert choreo.body_mass == 70.0
    assert choreo.total_time == pytest.approx(3.0)
    assert choreo.yaw_inertia == pytest.approx(1.4)
    assert BodyFEMConfig().m_eff == pytest.approx(30.0)
    impact = ImpactConfig()
    for got, expected in (
        (impact.m_skin, 1.5),
        (impact.m_scapula, 3.0),
        (impact.m_ribcage, 10.0),
        (impact.m_organ, 15.0),
        (impact.m_spine, 40.5),
    ):
        assert got == pytest.approx(expected)


def test_param_raises_for_missing_section_or_key() -> None:
    with pytest.raises(KeyError):
        param("no_such_section", "body_mass")
    with pytest.raises(KeyError):
        param("body", "no_such_key")
