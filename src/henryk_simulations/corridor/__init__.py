"""Corridor two-body kinematic plausibility simulation.

Models a contested sequence of two-body movements in a 2 m corridor over 3 s:
pull, position-swap, throw, simultaneous neck-reach, 180 deg re-orientation.

Submodules:
    config         scenario, geometry, bodies, phase dataclasses with defaults
    kinematics     per-phase analytical computation (v, a, F, impulse, energy)
    references     biomechanical reference distributions (scipy.stats)
    plausibility   z-score and verdict against references
    sim            PyBullet driver, two humanoid URDFs, MP4 export
    plots          matplotlib figures (timeline, forces, distribution overlays)
"""

from henryk_simulations.corridor.config import (
    Bodies,
    Geometry,
    Phase,
    Scenario,
    default_scenario,
)
from henryk_simulations.corridor.kinematics import (
    PhaseResult,
    compute_phase_kinematics,
    compute_scenario,
)
from henryk_simulations.corridor.plausibility import (
    PlausibilityScore,
    Verdict,
    score_phase,
)
from henryk_simulations.corridor.references import (
    Reference,
    ReferenceLibrary,
    default_library,
)

__all__ = [
    "Bodies",
    "Geometry",
    "Phase",
    "PhaseResult",
    "PlausibilityScore",
    "Reference",
    "ReferenceLibrary",
    "Scenario",
    "Verdict",
    "compute_phase_kinematics",
    "compute_scenario",
    "default_library",
    "default_scenario",
    "score_phase",
]
