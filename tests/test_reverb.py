"""Guards for the corridor reflection filter."""

from __future__ import annotations

import numpy as np
import pytest

from henryk_simulations.corridor import (
    CorridorImpulseResponse,
    CorridorReverbConfig,
    apply_corridor_reverb,
    corridor_impulse_response,
)


def test_config_defaults() -> None:
    cfg = CorridorReverbConfig()
    assert cfg.corridor_width == 2.0
    assert cfg.corridor_length == 10.0


def test_impulse_response_is_well_formed() -> None:
    cir = corridor_impulse_response(CorridorReverbConfig())
    assert isinstance(cir, CorridorImpulseResponse)
    assert cir.ir.ndim == 1 and len(cir.ir) > 1
    assert np.isfinite(cir.ir).all()
    assert cir.n_images == (2 * 12 + 1) ** 2  # max_order 12, two wall pairs


def test_direct_tap_is_unity_at_zero() -> None:
    # the m = 0 image is the source itself - the direct path, a unit tap at t = 0
    cir = corridor_impulse_response(CorridorReverbConfig())
    assert cir.ir[0] == pytest.approx(1.0)
    assert cir.direct_distance == pytest.approx(1.0)


def test_response_carries_reflections() -> None:
    cir = corridor_impulse_response(CorridorReverbConfig())
    assert np.count_nonzero(cir.ir[1:]) > 10  # many reflection taps
    assert np.abs(cir.ir[1:]).max() < 1.0  # every reflection is below the direct
    assert cir.rt60 > 0.0


def test_reflections_decay_along_the_response() -> None:
    cir = corridor_impulse_response(CorridorReverbConfig())
    half = len(cir.ir) // 2
    assert np.abs(cir.ir[:half]).sum() > np.abs(cir.ir[half:]).sum()


def test_softer_walls_shorten_the_tail() -> None:
    live = corridor_impulse_response(CorridorReverbConfig(wall_reflection=0.9))
    dead = corridor_impulse_response(CorridorReverbConfig(wall_reflection=0.5))
    assert live.rt60 > dead.rt60


def test_apply_returns_the_full_convolution() -> None:
    cir = corridor_impulse_response(CorridorReverbConfig())
    sig = np.random.default_rng(0).standard_normal(4000)
    wet = apply_corridor_reverb(sig, CorridorReverbConfig())
    assert len(wet) == len(sig) + len(cir.ir) - 1
    assert np.isfinite(wet).all()


def test_apply_preserves_the_direct_sound() -> None:
    # before the first reflection arrives the wet signal is the dry signal -
    # the direct path is the unit tap at index 0
    cir = corridor_impulse_response(CorridorReverbConfig())
    first_reflection = int(np.argmax(cir.ir[1:] != 0.0)) + 1
    sig = np.random.default_rng(1).standard_normal(4000)
    wet = apply_corridor_reverb(sig, CorridorReverbConfig())
    assert wet[:first_reflection] == pytest.approx(sig[:first_reflection])
