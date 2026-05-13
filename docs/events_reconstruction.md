# Events Reconstruction - 3-Phase Corridor Sequence

## Scenario

The contested 3-second sequence in a 2 m corridor is decomposed into three discrete actions, each receiving a 1.0 s share of the total time budget. This is the minimum-phase decomposition that maps the claim onto separable physical motions while keeping the actor maximally charitable on time per action.

The corridor topology, with V = Victoria, A = Andrew:

```
pre-timer    |V A .. |       A has approached V; both stand near the apartment door
t = 0.0 s    |V A .. |       timer starts
t = 1.0 s    | .. VA |       after pull
t = 2.0 s    | .. AV*|       after swap+throw; V's back impacts elevator door (*)
t = 3.0 s    | .. VA |       after swap-back; A ends at elevator with back to it
```

Initial positions: V at x=0.1 m (apartment doorway), A at x=0.5 m (just inside the corridor, in front of V). Both face toward the elevator at +x. V's facing direction tracks A's relative bearing throughout, rotating 180 degrees each time A swaps to her other side.

## Phase 1 - Pull (1.0 s)

A retreats backward toward the elevator while pulling V along. V translates 1.5 m from x=0.1 to x=1.6. A retreats from x=0.5 to x=1.8, keeping V slightly behind. No rotation in this phase.

Per-phase kinematic demands derived from the triangular velocity profile:

- duration: 1.0 s
- V displacement: 1.5 m
- v_peak = 2 * 1.5 / 1.0 = **3.0 m/s** (10.8 km/h)
- a_peak = 4 * 1.5 / 1.0^2 = **6.0 m/s^2** (0.61 g)
- F_peak = 70 * 6.0 = **420 N**
- impulse = 70 * 3.0 = **210 N s**
- kinetic energy = 0.5 * 70 * 3.0^2 = **315 J**

Verdicts against reference distributions:

- peak acceleration vs recreational sprint (3.0 +/- 0.8 m/s^2): z = 3.75 - **extreme**
- peak force vs two-arm push (800 +/- 200 N): z = -1.9 - plausible
- kinetic energy vs 5 kg overhand throw (160 +/- 80 J): z = 1.94 - strained

## Phase 2 - Swap and throw (1.0 s)

Positions exchange. V advances 0.5 m further to the elevator door (x=1.6 -> x=2.0); A swaps to V's other side, moving from x=1.8 to x=1.5. V's back impacts the elevator door at the end of this phase. V rotates 180 degrees during the swap to keep facing A.

Per-phase kinematic demands:

- duration: 1.0 s
- V translation: 0.5 m -> v_peak = 1.0 m/s, a_peak = 2.0 m/s^2 (0.20 g), F_peak = 140 N, KE = 35 J
- V rotation: pi rad -> omega_peak = 2 * pi / 1.0 = **6.28 rad/s** (360 deg/s)

Verdicts:

- peak acceleration: z = -1.25 - plausible
- peak force: z = -3.3 - plausible
- kinetic energy: z = -1.56 - plausible
- peak yaw angular velocity vs standing pivot (3.5 +/- 1.0 rad/s): z = 2.78 - **implausible**

## Phase 3 - Swap back (1.0 s)

Positions exchange again. A advances to the elevator door (x=1.5 -> x=2.0) and rotates 180 degrees so his back faces the elevator. V steps left (x=2.0 -> x=1.5) and rotates another 180 degrees tracking A.

Per-phase kinematic demands:

- duration: 1.0 s
- A and V each translate ~0.5 m: v_peak = 1.0 m/s, a_peak = 2.0 m/s^2, F_peak ~ 180 N (on A), KE ~ 45 J
- A rotation: pi rad -> omega_peak = 6.28 rad/s
- V rotation: pi rad -> omega_peak = 6.28 rad/s

Verdicts:

- peak yaw angular velocity (A, voluntary standing pivot): z = 2.78 - **implausible**
- peak yaw angular velocity (V, imposed rotation): z = 2.78 - **implausible**

## Post-event disengagement (visual only, NOT a scored phase)

After the 3 s contested window, the MP4 renders an additional ~1.5 s of decorative aftermath: Victoria crouches forward and slides back through the apartment doorway, exiting the corridor. Andrew remains at the elevator door with his back to it. This trailing animation is rendering-only - it is **not** added to the Scenario's phase list, does not appear in the kinematic tables, and does not contribute to any plausibility score. It is included only because the verbatim claim ends with "and then she fell"; depicting that aftermath in the same clip makes the timeline more readable. The full MP4 therefore runs ~4.5 s while the kinematic analysis covers only the first 3.0 s.

## Aggregate verdict

| Demand | Value | Verdict |
|---|---|---|
| pull - peak acceleration | 6.0 m/s^2 (0.61 g) | extreme |
| pull - peak force | 420 N | plausible |
| pull - kinetic energy | 315 J | strained |
| swap-throw - peak acceleration | 2.0 m/s^2 | plausible |
| swap-throw - peak force | 140 N | plausible |
| swap-throw - kinetic energy | 35 J | plausible |
| swap-throw - peak yaw rate | 6.28 rad/s (360 deg/s) | implausible |
| swap-back - peak yaw rate | 6.28 rad/s (360 deg/s) | implausible |

One extreme finding (pull acceleration at 3.75 sigma above the recreational-sprint reference), one strained (pull kinetic energy), two implausible (both rotation rates at 2.78 sigma above the standing-pivot reference). The remaining four demands are plausible.

The decisive impossibilities are concentrated in:

- **Phase 1 acceleration**: dragging a 70 kg unanchored body at 6 m/s^2 requires either friction levels above the foot-on-tile coefficient (mu ~ 0.3 -> 412 N friction cap for V's feet, which is at the force boundary) or active leg drive from a non-cooperating subject, which is not consistent with the deadweight model.
- **Both rotation rates**: 360 deg/s peak yaw is 2.8 sigma above the population mean for voluntary standing pivots. Imposing this rate on a passive 70 kg subject through arm contact during simultaneous translation has no biomechanical precedent in the cited literature.

## Compared to the earlier 2-phase reading

The 2-phase reading (pull and swap-and-throw mixed into one 1.5 s window) produced all-plausible verdicts because the action time was less compressed. Splitting into 3 phases of 1.0 s each, as the explicit action sequence requires, raises the pull acceleration into the extreme band and the rotation rates into the implausible band.

The 3-phase model is the more faithful reconstruction of the verbatim claim. The verdict shift reflects an intrinsic physical fact: the more sub-actions you fit into 3 seconds, the higher the per-action peak demands must climb to stay within budget.

## What this analysis does not establish

- Whether the alleged motion actually occurred (only physical plausibility of the kinematic demands)
- Whether grip mechanics, joint kinematics or stance permit the specific arm trajectories required - only CoM and yaw kinematics analysed
- The impact-force on V's back at the elevator door (covered separately in `impact_analysis.md`)
- Whether friction at V's feet during the pull is sufficient to transmit 420 N without slipping - the analysis treats V as a CoM point mass

## See also

- `reports/corridor-plausibility.md` - full plausibility report with figures and reference citations
- `reports/figures/01-corridor-sim-passive.mp4` - PyBullet animation of the 3-phase trajectory
- `reports/figures/01-phase-timeline.png` - phase Gantt chart
- `reports/figures/01-verdict-summary.png` - z-score lollipop summary
- `reports/figures/01-acceleration-timeline.png`, `01-force-timeline.png`, `01-speed-timeline.png`, `01-impulse-timeline.png` - per-body time series
- `docs/impact_analysis.md` - impact-force analysis at the elevator door
- `references/biomechanics-sources.md` - bibliography for the reference distributions
