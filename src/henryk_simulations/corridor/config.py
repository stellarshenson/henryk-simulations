"""Scenario configuration: geometry, bodies, phase decomposition."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

PhaseKind = Literal["translate", "rotate", "reach"]
ResistanceModel = Literal["passive", "small"]


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


def default_scenario() -> Scenario:
    """Minimal 2-phase decomposition mapped directly to the verbatim claim.

    Corridor layout: apartment door at x=0, elevator door at x=2. Victoria
    starts at the apartment doorway, Andrew in the corridor near the elevator.

      t=0   |V .. A|       (initial)
      t=1.5 | .. AV *|     (after pull-throw, V impacts elevator)
      t=3.0 | .. VA |      (after reverse, A's back to elevator)

    'Pull' and 'swap and throw' are explicitly described as mixed in the claim
    framing, so they collapse into a single 'pull-throw' phase. The 'reverse'
    phase swaps positions back so Andrew ends with his back to the elevator.
    Each phase gets half the 3 s budget, the most charitable allocation.

    1. Pull-throw (V translates 2.0 m + rotates 360 deg)  1.5 s
    2. Reverse    (A rotates 180 deg + positions swap)    1.5 s

    Victoria's 360 deg rotation in phase 1 has her back impact the elevator
    door (180 deg) then her front face Andrew again (another 180 deg).
    """
    import math

    phases = (
        Phase("pull-throw", 1.5, "translate", "M", translation=2.0, rotation=2 * math.pi),
        Phase("reverse", 1.5, "rotate", "H", rotation=math.pi),
    )
    return Scenario(
        total_time=3.0,
        geometry=Geometry(),
        bodies=Bodies(),
        phases=phases,
    )
