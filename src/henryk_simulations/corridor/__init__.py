"""Corridor two-body kinematic plausibility simulation.

Models a contested sequence of two-body movements in a 2 m corridor over 3 s:
pull, position-swap, throw, simultaneous neck-reach, 180 deg re-orientation.

Submodules:
    config         scenario, geometry, bodies, phase dataclasses with defaults
    kinematics     per-phase analytical computation (v, a, F, impulse, energy)
    acoustics      plate modes, cavity coupling, SPL prediction for door impact
    references     biomechanical reference distributions (scipy.stats)
    plausibility   z-score and verdict against references
    sim            PyBullet driver, two humanoid URDFs, MP4 export
    plots          matplotlib figures (timeline, forces, distribution overlays)
"""

from henryk_simulations.corridor.acoustics import (
    DEFAULT_ELEVATOR_DOOR,
    DEFAULT_ETA_RANGE,
    DEFAULT_LISTENERS,
    REF_SOUNDS,
    AcousticPrediction,
    AcousticSource,
    DoorGeometry,
    MaterialProps,
    PlateMode,
    PlatePanel,
    cavity_axial_frequency,
    frequency_band,
    plate_modes,
    predict_signature,
    spl_at_distance,
)
from henryk_simulations.corridor.choreography import (
    ChoreographyConfig,
    ChoreographyResult,
    Constraint,
    FreeParameter,
    ImpactSingularity,
    PhaseTrajectory,
    constraints,
    free_parameters,
    impact_singularity,
    solve_choreography,
    solve_envelope,
)
from henryk_simulations.corridor.config import (
    DEFAULT_PHASE_DURATIONS,
    Bodies,
    Geometry,
    Phase,
    Scenario,
    default_scenario,
)
from henryk_simulations.corridor.impact import (
    BodySegment,
    ContactPatch,
    EffectiveMass,
    FractureThreshold,
    FractureVerdict,
    ImpactConfig,
    ImpactDynamicsResult,
    assess_fracture,
    body_segments,
    contact_area,
    effective_impact_mass,
    fracture_thresholds,
    ribs_engaged,
    solve_impact,
    solve_impact_envelope,
)
from henryk_simulations.corridor.kinematics import (
    ImpactResult,
    PhaseResult,
    compute_impact,
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
    "DEFAULT_ELEVATOR_DOOR",
    "DEFAULT_ETA_RANGE",
    "DEFAULT_LISTENERS",
    "DEFAULT_PHASE_DURATIONS",
    "REF_SOUNDS",
    "AcousticPrediction",
    "AcousticSource",
    "Bodies",
    "BodySegment",
    "ChoreographyConfig",
    "ChoreographyResult",
    "Constraint",
    "ContactPatch",
    "DoorGeometry",
    "EffectiveMass",
    "FractureThreshold",
    "FractureVerdict",
    "FreeParameter",
    "Geometry",
    "ImpactConfig",
    "ImpactDynamicsResult",
    "ImpactResult",
    "ImpactSingularity",
    "MaterialProps",
    "Phase",
    "PhaseResult",
    "PhaseTrajectory",
    "PlateMode",
    "PlatePanel",
    "PlausibilityScore",
    "Reference",
    "ReferenceLibrary",
    "Scenario",
    "Verdict",
    "assess_fracture",
    "body_segments",
    "cavity_axial_frequency",
    "compute_impact",
    "compute_phase_kinematics",
    "compute_scenario",
    "constraints",
    "contact_area",
    "default_library",
    "default_scenario",
    "effective_impact_mass",
    "fracture_thresholds",
    "free_parameters",
    "frequency_band",
    "impact_singularity",
    "plate_modes",
    "predict_signature",
    "ribs_engaged",
    "score_phase",
    "solve_choreography",
    "solve_envelope",
    "solve_impact",
    "solve_impact_envelope",
    "spl_at_distance",
]
