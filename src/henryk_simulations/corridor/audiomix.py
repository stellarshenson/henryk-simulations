"""Event-audio augmentation - the synthesized impact sounds mixed into the recording.

Notebook 05's model. Notebooks 03 and 04 synthesize the two impact sounds -
the body thump and the door clang. This module places those sounds into the
real event recording (``event_recording.m4a``) at a configurable moment, so
the augmented recording carries the impact sound the original capture is
being tested against.

The loudest sample of each synthesized sound is aligned to a configurable
instant in the event timeline (default 0.15 s). The event recording and the
two synthesized tracks are summed, the result tanh soft-limited, and
encoded back to ``augmented_event_recording.m4a``.

The m4a decode and encode use the ffmpeg binary bundled with
``imageio-ffmpeg`` - no system ffmpeg is required.

Pipeline: ``decode_audio`` (event) and ``load_synth_sound`` x2 ->
``align_peak`` x2 -> sum and peak-limit -> ``encode_m4a``. ``augment_event``
runs the whole chain.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess

import imageio_ffmpeg
import numpy as np
from scipy.io import wavfile

from henryk_simulations.config import PROJ_ROOT
from henryk_simulations.corridor.simconfig import section_field

_param = section_field("audiomix")
_acoustics = section_field("acoustics")


@dataclass(frozen=True)
class AudioMixConfig:
    """Configuration for the event-audio augmentation."""

    event_path: str = "data/external/event_audio/event_recording.m4a"
    thump_path: str = "reports/figures/03-body-thump.wav"  # notebook 03 body thump
    clang_path: str = "reports/figures/04-door-clang.wav"  # notebook 04 door clang
    output_path: str = "reports/figures/augmented_event_recording.m4a"
    peak_time: float = _param(
        "peak_time"
    )  # s, event-timeline instant the synthesized peaks land on
    # recording timestamps are arbitrary - the event timeline is referenced to
    # the moment the toy is released
    toy_release_time: float = _param(
        "toy_release_time"
    )  # s, the toy is released - the timeline reference
    scream_time: float = _param("scream_time")  # s, the scream heard in the recording
    thump_gain: float = _param("thump_gain")  # linear gain on the body thump - boosted, the
    #                          low-frequency thump otherwise reads quiet (the
    #                          recording microphone's auto-gain lifts it too)
    clang_gain: float = _param("clang_gain")  # linear gain on the door clang
    sample_rate: int = _acoustics("sample_rate")  # Hz, working sample rate
    output_bitrate: str = "192k"  # AAC bitrate of the augmented m4a
    headroom: float = _param("headroom")  # peak the mix is normalised down to if it would clip


@dataclass(frozen=True)
class AudioMixResult:
    """Solved event-audio augmentation."""

    config: AudioMixConfig
    sample_rate: int
    event: np.ndarray  # the decoded event recording
    thump_track: np.ndarray  # the body thump, aligned to the event timeline
    clang_track: np.ndarray  # the door clang, aligned to the event timeline
    mixed: np.ndarray  # event + thump + clang, tanh soft-limited
    peak_index: int  # sample index the synthesized peaks land on
    peak_raw: float  # peak of the raw event+thump+clang sum, before the soft limiter


def _ffmpeg() -> str:
    """Path to the ffmpeg binary bundled with imageio-ffmpeg."""
    return imageio_ffmpeg.get_ffmpeg_exe()


def _resolve(path_str: str) -> Path:
    """Resolve a possibly-relative path against the project root."""
    path = Path(path_str)
    return path if path.is_absolute() else PROJ_ROOT / path


def decode_audio(path: str, sample_rate: int) -> np.ndarray:
    """Decode any audio file to a mono float signal at ``sample_rate``.

    ffmpeg decodes the file (m4a, wav, ...) to single-channel 32-bit float
    PCM at the requested rate; the raw stream is read straight into numpy.
    """
    cmd = [
        _ffmpeg(),
        "-v",
        "error",
        "-i",
        str(_resolve(path)),
        "-ac",
        "1",
        "-ar",
        str(sample_rate),
        "-f",
        "f32le",
        "-",
    ]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="<f4").astype(np.float64)


def load_synth_sound(path: str, sample_rate: int) -> np.ndarray:
    """Load a synthesized WAV (a notebook 03 / 04 output) as a mono float signal.

    The WAV is read, collapsed to mono and scaled to the [-1, 1] float range.
    Its sample rate must match the working rate.
    """
    sr, data = wavfile.read(_resolve(path))
    if sr != sample_rate:
        raise ValueError(f"{path} is {sr} Hz, expected {sample_rate} Hz")
    dtype = data.dtype
    data = np.asarray(data, dtype=np.float64)
    if data.ndim > 1:
        data = data.mean(axis=1)
    if np.issubdtype(dtype, np.integer):
        data = data / float(np.iinfo(dtype).max)
    return data


def align_peak(sound: np.ndarray, peak_index: int, total_len: int) -> np.ndarray:
    """Lay a sound onto an empty track so its loudest sample sits at ``peak_index``.

    The track is ``total_len`` samples of silence; the sound is positioned so
    that ``argmax(abs(sound))`` falls on ``peak_index``. A synthesized sound
    carries a silent lead-in, so aligning by the peak rather than the start
    places the impact itself on the requested instant; any part that would
    fall outside the track is trimmed.
    """
    track = np.zeros(total_len)
    if sound.size == 0 or total_len == 0:
        return track
    src_peak = int(np.argmax(np.abs(sound)))
    start = peak_index - src_peak
    lo = max(0, start)
    hi = min(total_len, start + len(sound))
    if lo < hi:
        track[lo:hi] = sound[lo - start : hi - start]
    return track


def mix_event(cfg: AudioMixConfig | None = None) -> AudioMixResult:
    """Mix the synthesized impact sounds into the event recording.

    The event recording is decoded; the body thump and door clang are loaded,
    gained, and laid onto the event timeline with their peaks on
    ``cfg.peak_time``; the three are summed and passed through a tanh soft
    limiter scaled to ``cfg.headroom``. The soft limiter is deliberate - a
    linear rescale of the sum to a fixed peak exactly cancels any gain
    applied to the loudest element, so the per-sound gains would have no
    audible effect; tanh saturation keeps them monotonic and audible.
    """
    if cfg is None:
        cfg = AudioMixConfig()
    event = decode_audio(cfg.event_path, cfg.sample_rate)
    thump = load_synth_sound(cfg.thump_path, cfg.sample_rate) * cfg.thump_gain
    clang = load_synth_sound(cfg.clang_path, cfg.sample_rate) * cfg.clang_gain

    n = len(event)
    peak_index = int(round(cfg.peak_time * cfg.sample_rate))
    thump_track = align_peak(thump, peak_index, n)
    clang_track = align_peak(clang, peak_index, n)

    raw = event + thump_track + clang_track
    peak_raw = float(np.abs(raw).max())
    # tanh soft limiter - keeps the per-sound gains audible (a linear rescale
    # to a fixed peak would cancel them), and its harmonics lift the
    # low-frequency thump into a more audible band.
    mixed = cfg.headroom * np.tanh(raw)
    return AudioMixResult(
        config=cfg,
        sample_rate=cfg.sample_rate,
        event=event,
        thump_track=thump_track,
        clang_track=clang_track,
        mixed=mixed,
        peak_index=peak_index,
        peak_raw=peak_raw,
    )


def encode_m4a(signal: np.ndarray, path: str, sample_rate: int, bitrate: str = "192k") -> Path:
    """Encode a mono float signal to an AAC ``.m4a`` file via ffmpeg."""
    pcm = np.clip(signal, -1.0, 1.0).astype("<f4").tobytes()
    out = _resolve(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        _ffmpeg(),
        "-v",
        "error",
        "-y",
        "-f",
        "f32le",
        "-ar",
        str(sample_rate),
        "-ac",
        "1",
        "-i",
        "pipe:0",
        "-c:a",
        "aac",
        "-b:a",
        bitrate,
        str(out),
    ]
    subprocess.run(cmd, input=pcm, check=True)
    return out


def augment_event(cfg: AudioMixConfig | None = None) -> AudioMixResult:
    """Augment the event recording with the synthesized impact sounds.

    Runs ``mix_event`` and encodes the result to ``cfg.output_path``.
    """
    if cfg is None:
        cfg = AudioMixConfig()
    result = mix_event(cfg)
    encode_m4a(result.mixed, cfg.output_path, cfg.sample_rate, cfg.output_bitrate)
    return result


__all__ = [
    "AudioMixConfig",
    "AudioMixResult",
    "align_peak",
    "augment_event",
    "decode_audio",
    "encode_m4a",
    "load_synth_sound",
    "mix_event",
]
