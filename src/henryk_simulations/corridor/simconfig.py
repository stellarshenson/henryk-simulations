"""Externalized simulation parameters - layered defaults and override.

The corridor configuration dataclasses read their physical and scenario
field defaults from two YAML files, merged at import:

* the **library defaults** - ``simulation_config.yml`` shipped inside this
  package - the parameters fixed from published literature or an
  established model;
* the **user file** - ``simulation_config.yaml`` at the project root by
  default, overridable through the ``SIMULATION_CONFIG_PATH`` environment
  variable (set it in ``.env``) - the scenario parameters for the run.

The user file is merged over the library defaults (a value in the user
file wins). The merged set is validated against physical-plausibility
ranges by :func:`henryk_simulations.corridor.validation.validate` - a bad
parameter raises before any simulation runs.

Numerical and discretization parameters, file paths, RNG seeds and the
universal acoustic constants are NOT externalized - they keep plain
literal defaults in the dataclass source.
"""

from __future__ import annotations

from collections.abc import Callable
import dataclasses
import os
from pathlib import Path
from typing import Any

import yaml

from henryk_simulations.config import PROJ_ROOT
from henryk_simulations.corridor.validation import validate

# the library defaults ship at the package root, one level above this module
LIBRARY_CONFIG_PATH = Path(__file__).parent.parent / "simulation_config.yml"

# the user file - simulation_config.yaml at the project root, unless
# SIMULATION_CONFIG_PATH (loaded from .env) points elsewhere
_configured = Path(os.getenv("SIMULATION_CONFIG_PATH", "simulation_config.yaml"))
CONFIG_PATH = _configured if _configured.is_absolute() else PROJ_ROOT / _configured


def _read_yaml(path: Path, label: str) -> dict[str, dict[str, Any]]:
    """Read one YAML config file, failing loud with a clear message."""
    try:
        with open(path, encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"{label} is required but missing: {path}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"{label} is malformed ({path}): {exc}") from exc


def _load() -> dict[str, dict[str, Any]]:
    """Load and merge the library defaults and the user file, then validate."""
    library = _read_yaml(LIBRARY_CONFIG_PATH, "library simulation_config.yml")
    user = _read_yaml(CONFIG_PATH, "simulation_config.yaml")
    # the user file is merged over the library defaults, per section;
    # `or {}` tolerates a section present-but-empty in either file
    merged: dict[str, dict[str, Any]] = {}
    for section in set(library) | set(user):
        merged[section] = {
            **(library.get(section) or {}),
            **(user.get(section) or {}),
        }
    validate(merged)
    return merged


_PARAMS: dict[str, dict[str, Any]] = _load()


def param(section: str, key: str) -> Any:
    """Return one externalized parameter, failing loud if it is absent."""
    try:
        values = _PARAMS[section]
    except KeyError as exc:
        raise KeyError(
            f"simulation config has no section '{section}' (have: {sorted(_PARAMS)})"
        ) from exc
    try:
        return values[key]
    except KeyError as exc:
        raise KeyError(
            f"simulation config section '{section}' has no key '{key}' (have: {sorted(values)})"
        ) from exc


def section_field(section: str) -> Callable[[str], Any]:
    """Return a dataclass-field factory bound to one config section.

    Each field built by the returned factory reads its default from the
    merged simulation config at instance construction time, so
    ``frozen=True``, explicit keyword arguments and ``dataclasses.replace``
    all keep working unchanged.
    """

    def make(key: str) -> Any:
        return dataclasses.field(default_factory=lambda k=key: param(section, k))

    return make


__all__ = ["CONFIG_PATH", "LIBRARY_CONFIG_PATH", "param", "section_field"]
