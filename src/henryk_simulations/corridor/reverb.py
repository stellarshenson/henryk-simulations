"""Corridor acoustics - propagation and reflections in the 2 m corridor.

A post-processing filter for the synthesized impact sounds. The 1 m
microphone signal from the FEM models (the body thump of notebook 03, the
door clang of notebook 04) is the direct path only; in the real corridor
the sound also reflects off the walls. The corridor is a 2 m x 10 m space -
the two side walls 2 m apart, the E and W end walls about 10 m apart - and
those four reflective surfaces add an early-reflection pattern and a
reverberant tail (the closely spaced side walls give the characteristic
corridor flutter echo).

The reflections are modelled by the image-source method: each wall mirrors
the source, every mirror image radiates a delayed, distance-attenuated and
reflection-attenuated copy of the sound to the microphone, and the images
are assembled into an impulse response. ``apply_corridor_reverb`` convolves
the dry signal with that response - the direct sound passes through
unchanged (the t = 0 tap) and the reflections are layered on after it.

Pipeline: ``corridor_impulse_response`` builds the response,
``apply_corridor_reverb`` convolves a dry signal with it.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.signal import fftconvolve

from henryk_simulations.corridor.simconfig import section_field

_param = section_field("reverb")
_acoustics = section_field("acoustics")


@dataclass(frozen=True)
class CorridorReverbConfig:
    """Configuration for the corridor reflection filter."""

    # corridor box - the two reflective wall pairs
    corridor_width: float = _param("corridor_width")  # m, between the two side walls
    corridor_length: float = _param("corridor_length")  # m, between the E and W end walls
    # impact source and microphone, in corridor coordinates (x across the
    # width, y along the length)
    source_x: float = _param("source_x")  # m, impact source across the width (corridor centre)
    source_y: float = _param("source_y")  # m, impact source along the length (near one end)
    mic_x: float = _param("mic_x")  # m, microphone across the width
    mic_y: float = _param("mic_y")  # m, microphone along the length - 1 m from the source
    # reflection
    wall_reflection: float = _param(
        "wall_reflection"
    )  # amplitude reflection coefficient per bounce
    max_order: int = 12  # image-source order per wall pair
    # acoustics
    air_c: float = _acoustics("air_c")  # m/s
    sample_rate: int = _acoustics("sample_rate")  # Hz


@dataclass(frozen=True)
class CorridorImpulseResponse:
    """The corridor's reflection impulse response."""

    ir: np.ndarray  # the impulse response - direct tap at index 0, reflections after
    sample_rate: int  # Hz
    n_images: int  # image sources summed into the response
    direct_distance: float  # m, the direct source-to-microphone path
    rt60: float  # s, reverberation time (T30-extrapolated energy -60 dB)


def _image_positions_1d(coord: float, span: float, order: int) -> list[tuple[float, int]]:
    """1D image-source coordinates between two walls, with reflection counts.

    For a source at ``coord`` between walls at 0 and ``span``, image ``m``
    sits at ``m*span + coord`` when ``m`` is even and ``(m+1)*span - coord``
    when ``m`` is odd; it carries ``|m|`` wall reflections. ``m = 0`` is the
    source itself.
    """
    out: list[tuple[float, int]] = []
    for m in range(-order, order + 1):
        if m % 2 == 0:
            pos = m * span + coord
        else:
            pos = (m + 1) * span - coord
        out.append((pos, abs(m)))
    return out


def _rt60(ir: np.ndarray, sample_rate: int) -> float:
    """Reverberation time of an impulse response - the T30 extrapolation.

    The Schroeder backward energy integral is taken, and the slope of its
    decay between -5 and -35 dB is extrapolated to a 60 dB fall.
    """
    energy = ir.astype(float) ** 2
    schroeder = np.cumsum(energy[::-1])[::-1]
    if schroeder[0] <= 0.0:
        return 0.0
    db = 10.0 * np.log10(np.maximum(schroeder / schroeder[0], 1e-12))
    t = np.arange(len(ir)) / sample_rate
    below5 = np.where(db <= -5.0)[0]
    below35 = np.where(db <= -35.0)[0]
    if below5.size == 0 or below35.size == 0:
        return 0.0
    i5, i35 = int(below5[0]), int(below35[0])
    if i35 <= i5:
        return 0.0
    slope = (db[i35] - db[i5]) / (t[i35] - t[i5])  # dB per second, negative
    return float(-60.0 / slope) if slope < 0 else 0.0


def corridor_impulse_response(
    cfg: CorridorReverbConfig | None = None,
) -> CorridorImpulseResponse:
    """Build the corridor's reflection impulse response by the image method.

    The source is mirrored across the two wall pairs up to ``max_order`` in
    each; every image radiates a tap delayed by its extra path length,
    attenuated by spherical spreading (``1/distance``) and by the wall
    reflection coefficient raised to the image's reflection count. The
    direct path is the ``m = 0`` image and lands at index 0 with unit
    amplitude, so convolving leaves the direct sound unchanged.
    """
    if cfg is None:
        cfg = CorridorReverbConfig()
    xs = _image_positions_1d(cfg.source_x, cfg.corridor_width, cfg.max_order)
    ys = _image_positions_1d(cfg.source_y, cfg.corridor_length, cfg.max_order)
    d_direct = float(np.hypot(cfg.source_x - cfg.mic_x, cfg.source_y - cfg.mic_y))

    taps: list[tuple[float, float]] = []  # (delay_s, amplitude)
    for x_img, n_x in xs:
        for y_img, n_y in ys:
            d = float(np.hypot(x_img - cfg.mic_x, y_img - cfg.mic_y))
            amp = cfg.wall_reflection ** (n_x + n_y) * d_direct / max(d, 1e-6)
            taps.append(((d - d_direct) / cfg.air_c, amp))

    n = int(np.ceil(max(delay for delay, _ in taps) * cfg.sample_rate)) + 1
    ir = np.zeros(n)
    for delay, amp in taps:
        idx = int(round(delay * cfg.sample_rate))
        if 0 <= idx < n:
            ir[idx] += amp

    return CorridorImpulseResponse(
        ir=ir,
        sample_rate=cfg.sample_rate,
        n_images=len(taps),
        direct_distance=d_direct,
        rt60=_rt60(ir, cfg.sample_rate),
    )


def apply_corridor_reverb(
    signal: np.ndarray, cfg: CorridorReverbConfig | None = None
) -> np.ndarray:
    """Filter a dry signal through the corridor's reflections.

    The dry 1 m-microphone signal is convolved with the corridor impulse
    response; the returned signal carries the direct sound followed by the
    reflections and the reverberant tail, so it is longer than the input by
    the length of the impulse response.
    """
    if cfg is None:
        cfg = CorridorReverbConfig()
    cir = corridor_impulse_response(cfg)
    return fftconvolve(np.asarray(signal, dtype=float), cir.ir)


__all__ = [
    "CorridorImpulseResponse",
    "CorridorReverbConfig",
    "apply_corridor_reverb",
    "corridor_impulse_response",
]
