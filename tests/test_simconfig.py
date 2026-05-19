"""Tests for the externalized simulation configuration.

The corridor config dataclasses read their physical/scenario field
defaults from two merged YAML files - the library `simulation_config.yml`
(literature defaults) and the user `simulation_config.yaml` (scenario).
These guards keep the merged config and the dataclasses in lockstep, and
check that the physics-linked quantities (total_time, yaw_inertia, m_eff,
the 5-DOF chain) derive correctly rather than being free parameters that
could drift out of sync.
"""

from __future__ import annotations

import dataclasses

import pytest

from henryk_simulations.corridor import simconfig
from henryk_simulations.corridor.audiomix import AudioMixConfig
from henryk_simulations.corridor.bodyfem import BodyFEMConfig
from henryk_simulations.corridor.choreography import ChoreographyConfig
from henryk_simulations.corridor.doorfem import DoorFEMConfig
from henryk_simulations.corridor.impact import ImpactConfig
from henryk_simulations.corridor.reverb import CorridorReverbConfig

# config dataclass keyed by the config section it owns
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


def _config() -> dict:
    """The merged, validated simulation config (library defaults + user file)."""
    return simconfig._PARAMS


def _factory_fields(config_cls: type) -> set[str]:
    """Field names whose default is read from the config."""
    return {
        f.name
        for f in dataclasses.fields(config_cls)
        if f.default_factory is not dataclasses.MISSING
    }


def test_config_has_expected_sections() -> None:
    assert set(_config()) == ALL_SECTIONS


def test_library_and_user_files_both_merged() -> None:
    """The merged config carries both a library default and a user value."""
    body = _config()["body"]
    assert "yaw_inertia_per_kg" in body  # from the library simulation_config.yml
    assert "body_mass" in body  # from the user simulation_config.yaml


@pytest.mark.parametrize("section", sorted(OWN_SECTION))
def test_every_field_resolves_to_exactly_one_key(section: str) -> None:
    """Each config-backed field reads from exactly one section, value matching."""
    data = _config()
    cfg = OWN_SECTION[section]()
    for name in _factory_fields(OWN_SECTION[section]):
        hits = [s for s in (section, *SHARED_SECTIONS) if name in data[s]]
        assert len(hits) == 1, f"{section}.{name} resolves to {hits}"
        assert getattr(cfg, name) == data[hits[0]][name]


def test_no_orphan_keys() -> None:
    """Every merged config key is consumed by some config field."""
    consumed: set[str] = set()
    for config_cls in OWN_SECTION.values():
        consumed |= _factory_fields(config_cls)
    for section, keys in _config().items():
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
    """The shipped config reproduces the 70 kg baseline (chain as fractions)."""
    choreo = ChoreographyConfig()
    assert choreo.body_mass == 70.0
    assert choreo.total_time == pytest.approx(3.0)
    assert choreo.yaw_inertia == pytest.approx(1.4)
    assert BodyFEMConfig().m_eff == pytest.approx(30.03)
    impact = ImpactConfig()
    for got, expected in (
        (impact.m_skin, 1.4),
        (impact.m_scapula, 2.8),
        (impact.m_ribcage, 9.8),
        (impact.m_organ, 15.4),
        (impact.m_spine, 40.6),
    ):
        assert got == pytest.approx(expected)


def test_param_raises_for_missing_section_or_key() -> None:
    with pytest.raises(KeyError):
        simconfig.param("no_such_section", "body_mass")
    with pytest.raises(KeyError):
        simconfig.param("body", "no_such_key")
