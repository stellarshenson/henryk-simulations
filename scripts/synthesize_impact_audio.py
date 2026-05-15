"""Synthesize the predicted acoustic signature of the contested impact.

Generates a short audio clip approximating what the phone microphone would have
recorded if Victoria's 70 kg body had hit the 2 mm steel elevator door at
3.21 m/s as the lower-bound reconstruction predicts.

Spectral content comes from `henryk_simulations.corridor.acoustics`:
- Door panel flexural modes (Kirchhoff, 6-24 Hz)
- Glass window modes (273-1093 Hz)
- Cavity axial mode (~5717 Hz)

Each mode is excited with a gamma-shaped envelope A(t) = (t/tau)^(k-1) exp(-t/tau),
giving fast rise and exponential decay - the canonical plate-strike transient shape.
Per-mode tau scales with frequency: long for steel and glass (high Q), short for
the trapped-air cavity mode (heavily damped).
"""

from __future__ import annotations

from pathlib import Path
import subprocess

import imageio_ffmpeg
import numpy as np
from scipy.io import wavfile

from henryk_simulations.corridor.acoustics import (
    DEFAULT_ELEVATOR_DOOR,
    cavity_axial_frequency,
    plate_modes,
)

SAMPLE_RATE = 44100
DURATION_S = 2.0
LEAD_SILENCE_S = 0.25  # short ambient context before the strike
STRIKE_OFFSET_S = LEAD_SILENCE_S

OUT_DIR = Path(__file__).resolve().parent.parent / "reports" / "figures"
OUT_WAV = OUT_DIR / "01-predicted-impact-audio.wav"
OUT_MP3 = OUT_DIR / "01-predicted-impact-audio.mp3"


def gamma_envelope(t: np.ndarray, tau: float, k: float = 2.0) -> np.ndarray:
    """Gamma envelope normalised so peak = 1.

    A(t) = (t/tau)^(k-1) * exp(-t/tau).  k=2 -> linear rise, exponential decay.
    """
    out = np.zeros_like(t)
    mask = t > 0
    ts = t[mask]
    peak_t = (k - 1.0) * tau
    peak_val = (peak_t / tau) ** (k - 1.0) * np.exp(-(k - 1.0)) if k > 1 else 1.0
    out[mask] = (ts / tau) ** (k - 1.0) * np.exp(-ts / tau) / peak_val
    return out


def synthesize_strike(t_rel: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Synthesize the impact transient.  t_rel = seconds since strike onset."""
    sig = np.zeros_like(t_rel)
    door = DEFAULT_ELEVATOR_DOOR

    # 1. Steel panel modes (6-24 Hz).  Sub-bass body of the impact; mostly felt
    #    not heard on small speakers, but renders as a deep thud on anything
    #    with low-end response.
    panel_modes = plate_modes(door.panel, n_max=4)[:6]
    for mode in panel_modes:
        f = mode.frequency_hz
        env = gamma_envelope(t_rel, tau=0.22, k=2.0)
        phase = rng.uniform(0, 2 * np.pi)
        sig += 0.55 * env * np.sin(2 * np.pi * f * t_rel + phase)

    # 2. Glass window modes (273-1093 Hz).  This is the audible "ring".  Higher
    #    modes scale down so the fundamental dominates.
    if door.window is not None:
        window_modes = plate_modes(door.window, n_max=4)[:6]
        f0 = window_modes[0].frequency_hz
        for mode in window_modes:
            f = mode.frequency_hz
            env = gamma_envelope(t_rel, tau=0.18, k=2.0)
            phase = rng.uniform(0, 2 * np.pi)
            amp = 0.70 * (f0 / f) ** 0.7
            sig += amp * env * np.sin(2 * np.pi * f * t_rel + phase)

    # 3. Cavity axial mode (~5717 Hz).  Bright "ting" from the trapped air
    #    between the two steel plates; short ring-down.
    f_cav = cavity_axial_frequency(door.cavity_gap_m)
    env_cav = gamma_envelope(t_rel, tau=0.04, k=2.0)
    sig += 0.45 * env_cav * np.sin(2 * np.pi * f_cav * t_rel)

    # 4. Short broadband contact "thwack" - the mechanical strike itself
    #    before the modes take over.  Filtered noise burst, 6 ms half-life,
    #    bandpassed by a wide gaussian envelope.
    contact_env = np.exp(-(t_rel - 0.003) ** 2 / (2 * 0.004**2)) * (t_rel >= 0)
    noise = rng.standard_normal(t_rel.size)
    sig += 0.25 * noise * contact_env
    return sig


def main() -> None:
    n_samples = int(SAMPLE_RATE * DURATION_S)
    t = np.arange(n_samples) / SAMPLE_RATE
    rng = np.random.default_rng(42)

    # Strike begins at t = LEAD_SILENCE_S so the listener hears context first.
    t_rel = t - STRIKE_OFFSET_S
    strike = synthesize_strike(t_rel, rng)

    # Mic self-noise / ambient hallway, throughout the clip (~ -50 dBFS).
    ambient = rng.standard_normal(n_samples) * 10 ** (-50 / 20)

    signal = strike + ambient

    # Peak-normalise to -1 dBFS (0.89).  Pure linear scaling; no limiter, no
    # clip - guaranteed within [-0.89, 0.89] so nothing ever saturates.
    peak = np.max(np.abs(signal))
    signal = signal / peak * 0.89

    audio_int16 = np.int16(signal * 32767)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    wavfile.write(str(OUT_WAV), SAMPLE_RATE, audio_int16)
    print(f"wrote {OUT_WAV} ({OUT_WAV.stat().st_size} bytes)")

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-loglevel", "error",
            "-i", str(OUT_WAV),
            "-codec:a", "libmp3lame",
            "-qscale:a", "2",
            str(OUT_MP3),
        ],
        check=True,
    )
    print(f"wrote {OUT_MP3} ({OUT_MP3.stat().st_size} bytes)")

    # Sanity check: report RMS of the strike segment vs ambient lead.
    lead_rms = np.sqrt(np.mean(signal[: int(SAMPLE_RATE * LEAD_SILENCE_S)] ** 2))
    strike_rms = np.sqrt(
        np.mean(signal[int(SAMPLE_RATE * LEAD_SILENCE_S) : int(SAMPLE_RATE * (LEAD_SILENCE_S + 0.5))] ** 2)
    )
    print(f"ambient RMS: {20 * np.log10(max(lead_rms, 1e-9)):.1f} dBFS")
    print(f"strike RMS:  {20 * np.log10(max(strike_rms, 1e-9)):.1f} dBFS")


if __name__ == "__main__":
    main()
