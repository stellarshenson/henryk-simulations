"""Acoustic signature of a blunt impact against a hollow plate-and-cavity door.

Computes plate flexural modal frequencies (Kirchhoff thin-plate theory),
half-wave cavity coupling, and peak sound-pressure-level (SPL) at one or more
listener distances given the mechanical impact source.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math

# === Material constants ===


@dataclass(frozen=True)
class MaterialProps:
    """Isotropic linear-elastic material."""

    E: float  # Young's modulus, Pa
    nu: float  # Poisson's ratio
    rho: float  # density, kg/m^3


STEEL = MaterialProps(E=200e9, nu=0.30, rho=7850)
GLASS = MaterialProps(E=70e9, nu=0.22, rho=2500)

C_AIR = 343.0  # speed of sound in air, m/s
I_REF = 1e-12  # reference intensity for SPL, W/m^2 (threshold of hearing)


# === Geometry ===


@dataclass(frozen=True)
class PlatePanel:
    """Thin rectangular plate, simply supported on its perimeter."""

    a_m: float
    b_m: float
    thickness_m: float
    material: MaterialProps


@dataclass(frozen=True)
class DoorGeometry:
    """Hollow door: two plates separated by an air cavity, with optional window."""

    panel: PlatePanel
    cavity_gap_m: float
    window: PlatePanel | None = None


DEFAULT_ELEVATOR_DOOR = DoorGeometry(
    panel=PlatePanel(a_m=2.0, b_m=1.0, thickness_m=0.002, material=STEEL),
    cavity_gap_m=0.03,
    window=PlatePanel(a_m=0.20, b_m=0.60, thickness_m=0.004, material=GLASS),
)


# === Source ===


@dataclass(frozen=True)
class AcousticSource:
    """Mechanical impact pulse that excites the panel."""

    peak_force_N: float
    stopping_distance_m: float
    contact_time_s: float

    @property
    def work_deposited_J(self) -> float:
        """Triangular force pulse work: 1/2 * F_peak * d_stop."""
        return 0.5 * self.peak_force_N * self.stopping_distance_m


# === Modal frequencies ===


@dataclass(frozen=True)
class PlateMode:
    m: int
    n: int
    frequency_hz: float


def plate_modes(panel: PlatePanel, n_max: int = 4) -> list[PlateMode]:
    """Flexural modal frequencies of a simply supported Kirchhoff plate.

    f_mn = (pi/2) sqrt(D / sigma) [(m/a)^2 + (n/b)^2]
        D     = E h^3 / (12 (1 - nu^2))     (flexural rigidity)
        sigma = rho h                       (areal density)
    """
    mat = panel.material
    D = mat.E * panel.thickness_m**3 / (12.0 * (1.0 - mat.nu**2))
    sigma = mat.rho * panel.thickness_m
    coeff = (math.pi / 2.0) * math.sqrt(D / sigma)
    modes = [
        PlateMode(
            m=m,
            n=n,
            frequency_hz=coeff * ((m / panel.a_m) ** 2 + (n / panel.b_m) ** 2),
        )
        for m in range(1, n_max + 1)
        for n in range(1, n_max + 1)
    ]
    modes.sort(key=lambda mode: mode.frequency_hz)
    return modes


def cavity_axial_frequency(gap_m: float, c_air: float = C_AIR) -> float:
    """First axial standing-wave frequency for a sealed cavity of depth gap_m.

    Half-wave resonator: f = c / (2 d).
    """
    return c_air / (2.0 * gap_m)


# === Sound-pressure-level prediction ===


def spl_at_distance(
    eta: float,
    work_J: float,
    contact_s: float,
    distance_m: float,
    i_ref: float = I_REF,
) -> float:
    """Peak SPL (dB re 20 uPa) from a short pulse, free field, omnidirectional.

    Acoustic power during the pulse: P_a = eta * W / t
    Free-field intensity at distance r: I = P_a / (4 pi r^2)
    SPL: L_p = 10 log10(I / I_ref)
    """
    p_acoustic = eta * work_J / contact_s
    intensity = p_acoustic / (4.0 * math.pi * distance_m * distance_m)
    return 10.0 * math.log10(intensity / i_ref)


# Radiation-efficiency bracket for a struck steel plate.
DEFAULT_ETA_RANGE: dict[str, float] = {
    "low (lossy mounting)": 0.001,
    "typical": 0.01,
    "high (well-coupled)": 0.05,
}

# Listener label + distance (m). Defaults pin Cecilia and the phone microphone
# in their reconstructed positions during the contested incident.
DEFAULT_LISTENERS: list[tuple[str, float]] = [
    ("door surface (~10 cm)", 0.10),
    ("Cecilia at ~1.5 m", 1.50),
    ("phone mic at ~2 m", 2.00),
]


@dataclass(frozen=True)
class AcousticPrediction:
    """End-to-end acoustic signature of an impact against a hollow door."""

    door: DoorGeometry
    source: AcousticSource
    door_modes: list[PlateMode]
    window_modes: list[PlateMode]
    cavity_axial_hz: float
    eta_range: dict[str, float]
    listeners: list[tuple[str, float]]
    spl_grid: dict[str, dict[str, float]] = field(default_factory=dict)
    """spl_grid[listener_label][eta_label] -> peak SPL in dB."""


def predict_signature(
    door: DoorGeometry,
    source: AcousticSource,
    *,
    eta_range: dict[str, float] | None = None,
    listeners: list[tuple[str, float]] | None = None,
    n_modes: int = 6,
) -> AcousticPrediction:
    """Compute the full acoustic prediction for a door/source pair."""
    etas = dict(eta_range) if eta_range is not None else dict(DEFAULT_ETA_RANGE)
    lst = list(listeners) if listeners is not None else list(DEFAULT_LISTENERS)

    door_modes = plate_modes(door.panel, n_max=4)[:n_modes]
    window_modes = plate_modes(door.window, n_max=4)[:n_modes] if door.window is not None else []
    cavity_hz = cavity_axial_frequency(door.cavity_gap_m)

    spl_grid: dict[str, dict[str, float]] = {}
    for listener_label, distance_m in lst:
        spl_grid[listener_label] = {
            eta_label: spl_at_distance(
                eta,
                source.work_deposited_J,
                source.contact_time_s,
                distance_m,
            )
            for eta_label, eta in etas.items()
        }

    return AcousticPrediction(
        door=door,
        source=source,
        door_modes=door_modes,
        window_modes=window_modes,
        cavity_axial_hz=cavity_hz,
        eta_range=etas,
        listeners=lst,
        spl_grid=spl_grid,
    )


# === Reference SPL benchmarks for axis annotation ===

REF_SOUNDS: list[tuple[int, str]] = [
    (60, "normal conversation at 1 m"),
    (90, "lawn mower at 1 m"),
    (110, "rock concert, front row"),
    (120, "pain threshold; phone-mic clipping"),
    (130, "jackhammer at 1 m"),
    (140, "jet engine at 30 m; gunshot at 5 m"),
    (160, "gunshot at 1 m; instant hearing damage"),
]


def frequency_band(frequency_hz: float) -> str:
    """Classify a frequency into a human-audible band."""
    if frequency_hz < 20:
        return "infrasound"
    if frequency_hz < 250:
        return "bass"
    if frequency_hz < 4000:
        return "midrange"
    if frequency_hz < 16000:
        return "treble"
    return "ultrasound"


__all__ = [
    "C_AIR",
    "DEFAULT_ELEVATOR_DOOR",
    "DEFAULT_ETA_RANGE",
    "DEFAULT_LISTENERS",
    "GLASS",
    "I_REF",
    "STEEL",
    "AcousticPrediction",
    "AcousticSource",
    "DoorGeometry",
    "MaterialProps",
    "PlateMode",
    "PlatePanel",
    "REF_SOUNDS",
    "cavity_axial_frequency",
    "frequency_band",
    "plate_modes",
    "predict_signature",
    "spl_at_distance",
]
