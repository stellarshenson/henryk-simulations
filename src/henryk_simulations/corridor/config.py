"""Scenario configuration: geometry, bodies, phase decomposition."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

PhaseKind = Literal["translate", "rotate", "reach"]
# Only the worst-case no-resistance model is kept; small-resistance was a
# strictly-friendlier variant for the actor and is no longer informative.
ResistanceModel = Literal["passive"]


@dataclass(frozen=True)
class Geometry:
    """Corridor geometry.

    The corridor runs from the apartment door (x=0) to the elevator door (x=corridor_width).
    Lateral extent is taken as 1.5 m to allow rotation and arm extension.
    """

    corridor_width: float = 2.0  # m, door-to-door
    corridor_lateral: float = 1.5  # m, side-wall to side-wall
    door_height: float = 2.1  # m
    floor_z: float = 0.0  # m


@dataclass(frozen=True)
class Bodies:
    """Body parameters."""

    h_mass: float = 90.0  # kg, Andrew
    m_mass: float = 70.0  # kg, Victoria
    standing_height_h: float = 1.80  # m
    standing_height_m: float = 1.68  # m
    # Whole-body moment of inertia about vertical (yaw) axis through CoM,
    # standing posture, segment-mass model (Plagenhoef 1983).
    yaw_inertia_h: float = 1.8  # kg*m^2 (scaled from 1.5 for larger mass)
    yaw_inertia_m: float = 1.4  # kg*m^2


@dataclass(frozen=True)
class Phase:
    """A single phase of the alleged motion.

    Attributes
    ----------
    name        short label
    duration    seconds
    kind        translate, rotate, or reach (arm extension)
    body        which body undergoes the motion ("H", "M", or "both")
    translation meters of centre-of-mass displacement (if kind == translate)
    rotation    radians of body rotation (if kind == rotate)
    reach       meters of arm extension (if kind == reach)
    overlaps_with index of an earlier phase that this one runs concurrently with;
                  if set, the phase consumes no additional time budget
    """

    name: str
    duration: float
    kind: PhaseKind
    body: Literal["H", "M", "both"]
    translation: float = 0.0
    rotation: float = 0.0
    reach: float = 0.0
    overlaps_with: int | None = None
    # Optional secondary motion: the other body's translation/rotation
    # within the same phase. Used e.g. for swap-back where V also
    # translates and rotates while A is the primary actor.
    other_translation: float = 0.0
    other_rotation: float = 0.0


@dataclass(frozen=True)
class Scenario:
    """Full scenario configuration."""

    total_time: float
    geometry: Geometry
    bodies: Bodies
    phases: tuple[Phase, ...]

    def __post_init__(self) -> None:
        sequential = sum(p.duration for p in self.phases if p.overlaps_with is None)
        if abs(sequential - self.total_time) > 1e-6:
            raise ValueError(
                f"Sequential phase durations sum to {sequential:.3f} s but "
                f"total_time is {self.total_time:.3f} s",
            )

    @property
    def phase_starts(self) -> list[float]:
        """Start time of each phase. Overlapping phases align to host phase's tail."""
        starts: list[float] = []
        cursor = 0.0
        for idx, phase in enumerate(self.phases):
            if phase.overlaps_with is None:
                starts.append(cursor)
                cursor += phase.duration
            else:
                host_start = starts[phase.overlaps_with]
                host_dur = self.phases[phase.overlaps_with].duration
                starts.append(host_start + host_dur - phase.duration)
        return starts


DEFAULT_PHASE_DURATIONS: dict[str, float] = {
    "pull": 1.0,
    "swap-throw": 1.0,
    "swap-back": 1.0,
}


def default_scenario(
    phase_durations: dict[str, float] | None = None,
) -> Scenario:
    """3-phase decomposition: pull, swap-and-throw, swap-back.

    Corridor layout: apartment door at x=0, elevator door at x=2. Before
    the timer starts, Andrew has approached Victoria. The timer begins when
    Andrew starts moving backward toward the elevator pulling her. V faces
    A throughout - her body rotation tracks A's relative bearing as
    positions swap.

      pre-timer    |V A .. |
      t = 0        |V A .. |       (timer starts)
      after pull   | .. VA |
      after swap   | .. AV*|       (V's back impacts elevator door)
      after swap   | .. VA |       (A ends at elevator with back to it)
      back

    Each phase has its own translation and rotation budget. Per-phase peak
    velocity, acceleration and force are determined entirely by the phase
    duration and displacement using a triangular velocity profile:
        v_peak = 2 * distance / duration
        a_peak = 4 * distance / duration^2

    Distances are V's CoM displacements. With a torso radius of 0.14 m, V's
    body surface (back) reaches the elevator door (x=2.0) when her CoM is at
    1.86 m. V's CoM total travel = 1.72 m (2.0 m corridor minus two torso
    radii since V is centred at her own torso while the corridor is measured
    door-to-door).

    Phase durations are configurable via `phase_durations` keyed by phase
    name. Defaults from `DEFAULT_PHASE_DURATIONS` allocate 1.0 s each over a
    3.0 s total. Override any subset; `total_time` is recomputed as the sum.

    Examples:
        default_scenario()                              # 1.0 s each
        default_scenario({"pull": 1.5, "swap-throw": 0.8, "swap-back": 0.7})
        default_scenario({"pull": 1.5})                 # rest stay at 1.0 s

    1. Pull        (V translates 1.5 m, no rotation)
    2. Swap+throw  (V translates 0.22 m + rotates 180 deg)
    3. Swap-back   (A rotates 180 deg + V rotates 180 deg + position swap)
    """
    import math

    durations = dict(DEFAULT_PHASE_DURATIONS)
    if phase_durations:
        unknown = set(phase_durations) - set(durations)
        if unknown:
            raise ValueError(f"unknown phase names in phase_durations: {sorted(unknown)}")
        for name, dur in phase_durations.items():
            if dur <= 0:
                raise ValueError(f"phase '{name}' duration must be positive, got {dur}")
            durations[name] = dur

    phases = (
        Phase("pull", durations["pull"], "translate", "M", translation=1.5),
        Phase(
            "swap-throw",
            durations["swap-throw"],
            "translate",
            "M",
            translation=0.22,
            rotation=math.pi,
        ),
        Phase(
            "swap-back",
            durations["swap-back"],
            "rotate",
            "H",
            rotation=math.pi,
            other_translation=0.40,  # V steps back 40 cm to end up in front of A
            other_rotation=math.pi,  # V rotates 180 deg to keep facing A
        ),
    )
    return Scenario(
        total_time=sum(durations.values()),
        geometry=Geometry(),
        bodies=Bodies(),
        phases=phases,
    )
