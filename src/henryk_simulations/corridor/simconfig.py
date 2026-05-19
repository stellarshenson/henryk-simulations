"""Externalized simulation parameters.

The corridor configuration dataclasses read their physical and scenario
field defaults from a documented YAML file - ``simulation_config.yaml`` at
the project root by default. The path is overridable through the
``SIMULATION_CONFIG_PATH`` environment variable (set it in ``.env``), so a
what-if run can point at an alternative parameter file without touching
the source. A relative path is resolved against ``PROJ_ROOT``. The file is
loaded once here at import.

Numerical and discretization parameters, file paths, RNG seeds and the
universal acoustic constants are NOT externalized - they keep plain
literal defaults in the dataclass source.

The default file is resolved against ``PROJ_ROOT``, so the project is
expected to run from a checkout (an editable install or the repo itself),
not from a bare installed wheel.
"""

from __future__ import annotations

from collections.abc import Callable
import dataclasses
import os
from pathlib import Path
from typing import Any

import yaml

from henryk_simulations.config import PROJ_ROOT

# the parameter file - simulation_config.yaml at the project root, unless
# SIMULATION_CONFIG_PATH (loaded from .env) points elsewhere
_configured = Path(os.getenv("SIMULATION_CONFIG_PATH", "simulation_config.yaml"))
CONFIG_PATH = _configured if _configured.is_absolute() else PROJ_ROOT / _configured


def _load() -> dict[str, dict[str, Any]]:
    """Load the simulation parameter file once, at import."""
    try:
        with open(CONFIG_PATH, encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"simulation_config.yaml is required but missing: {CONFIG_PATH}"
        ) from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"simulation_config.yaml is malformed ({CONFIG_PATH}): {exc}") from exc


_PARAMS: dict[str, dict[str, Any]] = _load()


def param(section: str, key: str) -> Any:
    """Return one externalized parameter, failing loud if it is absent."""
    try:
        values = _PARAMS[section]
    except KeyError as exc:
        raise KeyError(
            f"simulation_config.yaml has no section '{section}' (have: {sorted(_PARAMS)})"
        ) from exc
    try:
        return values[key]
    except KeyError as exc:
        raise KeyError(
            f"simulation_config.yaml section '{section}' has no key '{key}' "
            f"(have: {sorted(values)})"
        ) from exc


def section_field(section: str) -> Callable[[str], Any]:
    """Return a dataclass-field factory bound to one YAML section.

    Each field built by the returned factory reads its default from
    ``simulation_config.yaml`` at instance construction time, so
    ``frozen=True``, explicit keyword arguments and ``dataclasses.replace``
    all keep working unchanged.
    """

    def make(key: str) -> Any:
        return dataclasses.field(default_factory=lambda k=key: param(section, k))

    return make


__all__ = ["CONFIG_PATH", "param", "section_field"]
