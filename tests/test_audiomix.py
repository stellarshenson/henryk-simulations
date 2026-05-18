"""Guards for the event-audio augmentation module."""

from __future__ import annotations

import dataclasses

import numpy as np
import pytest

from henryk_simulations.corridor import (
    AudioMixConfig,
    AudioMixResult,
    align_peak,
    augment_event,
    decode_audio,
    load_synth_sound,
    mix_event,
)


@pytest.fixture(scope="module")
def mixed() -> AudioMixResult:
    return mix_event(AudioMixConfig())


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


def test_config_defaults() -> None:
    cfg = AudioMixConfig()
    assert cfg.peak_time == 15.0
    assert cfg.toy_release_time == 12.5
    assert cfg.scream_time == 16.5
    assert cfg.sample_rate == 44100
    assert cfg.output_path.endswith("augmented_event_recording.m4a")


# ---------------------------------------------------------------------------
# Peak alignment
# ---------------------------------------------------------------------------


def test_align_peak_places_peak_at_index() -> None:
    sound = np.array([0.0, 0.2, 1.0, 0.3, 0.0])  # loudest sample at index 2
    track = align_peak(sound, peak_index=100, total_len=500)
    assert len(track) == 500
    assert int(np.argmax(np.abs(track))) == 100


def test_align_peak_clips_negative_start() -> None:
    sound = np.array([0.1, 0.5, 1.0, 0.4])  # peak index 2, start would be -1
    track = align_peak(sound, peak_index=1, total_len=50)
    assert len(track) == 50
    assert int(np.argmax(np.abs(track))) == 1


def test_align_peak_clips_past_end() -> None:
    sound = np.array([0.1, 1.0, 0.2])
    track = align_peak(sound, peak_index=49, total_len=50)
    assert len(track) == 50
    assert np.isfinite(track).all()


def test_align_peak_empty_sound() -> None:
    track = align_peak(np.array([]), peak_index=10, total_len=100)
    assert len(track) == 100
    assert not track.any()


# ---------------------------------------------------------------------------
# Decode and load
# ---------------------------------------------------------------------------


def test_decode_event_recording() -> None:
    cfg = AudioMixConfig()
    event = decode_audio(cfg.event_path, cfg.sample_rate)
    assert event.ndim == 1
    assert len(event) > cfg.sample_rate  # at least a second of audio
    assert np.isfinite(event).all()


def test_load_synth_sounds_are_normalised() -> None:
    cfg = AudioMixConfig()
    for path in (cfg.thump_path, cfg.clang_path):
        sig = load_synth_sound(path, cfg.sample_rate)
        assert sig.ndim == 1
        assert np.abs(sig).max() <= 1.0
        assert np.isfinite(sig).all()


def test_load_synth_sound_rejects_wrong_rate() -> None:
    cfg = AudioMixConfig()
    with pytest.raises(ValueError):
        load_synth_sound(cfg.thump_path, 22050)


# ---------------------------------------------------------------------------
# Mixing
# ---------------------------------------------------------------------------


def test_mix_length_matches_event(mixed: AudioMixResult) -> None:
    assert len(mixed.mixed) == len(mixed.event)
    assert len(mixed.thump_track) == len(mixed.event)
    assert len(mixed.clang_track) == len(mixed.event)


def test_mix_peak_index_on_peak_time(mixed: AudioMixResult) -> None:
    cfg = mixed.config
    assert mixed.peak_index == round(cfg.peak_time * cfg.sample_rate)


def test_synth_tracks_peak_on_the_aligned_moment(mixed: AudioMixResult) -> None:
    assert int(np.argmax(np.abs(mixed.thump_track))) == mixed.peak_index
    assert int(np.argmax(np.abs(mixed.clang_track))) == mixed.peak_index


def test_mix_stays_within_headroom(mixed: AudioMixResult) -> None:
    assert np.abs(mixed.mixed).max() <= mixed.config.headroom + 1e-9
    assert mixed.peak_raw > 0.0


def test_thump_gain_changes_the_mix() -> None:
    # the tanh soft limiter keeps the per-sound gains audible - a louder
    # thump_gain must raise the energy of the mix at the impact
    soft = mix_event(dataclasses.replace(AudioMixConfig(), thump_gain=1.0))
    loud = mix_event(dataclasses.replace(AudioMixConfig(), thump_gain=4.0))
    window = slice(soft.peak_index, soft.peak_index + soft.sample_rate)
    soft_rms = float(np.sqrt(np.mean(soft.mixed[window] ** 2)))
    loud_rms = float(np.sqrt(np.mean(loud.mixed[window] ** 2)))
    assert loud_rms > soft_rms


# ---------------------------------------------------------------------------
# Encode and augment
# ---------------------------------------------------------------------------


def test_augment_event_writes_m4a(tmp_path) -> None:
    out = tmp_path / "augmented.m4a"
    cfg = dataclasses.replace(AudioMixConfig(), output_path=str(out))
    result = augment_event(cfg)
    assert isinstance(result, AudioMixResult)
    assert out.exists() and out.stat().st_size > 0
    # the encoded file decodes back to roughly the same duration
    back = decode_audio(str(out), cfg.sample_rate)
    assert abs(len(back) - len(result.mixed)) < cfg.sample_rate  # within 1 s
