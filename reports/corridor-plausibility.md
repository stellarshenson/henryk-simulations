# Corridor Two-Body Plausibility Verdict

## Overview

A 3-phase analytical decomposition of the contested 3-second corridor sequence finds that one of eight scored kinematic demands falls in the extreme band (z > 3) and two in the implausible band (2 < z <= 3). The decisive findings are: peak acceleration of 6.0 m/s^2 (0.61 g) imposed on Victoria during the pull phase, 3.75 standard deviations above the recreational-sprint reference; and the peak yaw angular velocities of 6.28 rad/s (~360 deg/s) required for both Victoria and Andrew during the two swap phases, each 2.78 standard deviations above the standing-pivot reference. Force and energy demands sit in the plausible band.

## Scenario configuration

```
pre-timer    |V A .. |       (A has approached V; both near apartment door)
t = 0.0 s    |V A .. |       (timer starts)
t = 1.0 s    | .. VA |       (after pull: A retreats to elevator pulling V)
t = 2.0 s    | .. AV*|       (after swap+throw: V's back impacts elevator door)
t = 3.0 s    | .. VA |       (after swap-back: A ends at elevator with back to it)
```

- Corridor width (apartment door to elevator door) 2.0 m, lateral 1.5 m
- Andrew 90 kg standing 1.80 m, initial position x=0.5 m (just inside the corridor, in front of V)
- Victoria 70 kg standing 1.68 m, initial position x=0.1 m (apartment doorway)
- Both face the elevator initially (+x). Victoria's facing direction rotates 180 deg per swap phase tracking Andrew

Three phases, 1.0 s each:

- **Pull** 1.0 s. Andrew retreats backward toward the elevator pulling Victoria along. Victoria translates 1.5 m. No rotation in this phase
- **Swap+throw** 1.0 s. Positions exchange; Victoria advances 0.5 m further and her back impacts the elevator door. Victoria rotates 180 deg
- **Swap-back** 1.0 s. Positions exchange again; Andrew rotates 180 deg so his back faces the elevator; Victoria rotates another 180 deg tracking Andrew

Full event reconstruction in `docs/events_reconstruction.md`.

![Corridor geometry](figures/01-corridor-geometry.png)
![Phase timeline](figures/01-phase-timeline.png)

## Per-phase headline numbers

| Phase | Duration | v_peak | a_peak | F_peak | KE | impulse | omega_peak |
|---|---|---|---|---|---|---|---|
| pull | 1.0 s | 3.00 m/s | 6.00 m/s^2 (0.61 g) | 420 N | 315 J | 210 N s | - |
| swap-throw | 1.0 s | 1.00 m/s | 2.00 m/s^2 (0.20 g) | 140 N | 35 J | 70 N s | 6.28 rad/s |
| swap-back | 1.0 s | - | - | - | - | - | 6.28 rad/s |

## Phase-by-phase verdict

**Phase 1 - Pull (1.0 s, Victoria 1.5 m, no rotation).** Three scored quantities:

- Peak acceleration 6.0 m/s^2 (0.61 g), z=3.75 above recreational sprint reference - **extreme**
- Peak applied force 420 N, z=-1.9 below the two-arm push budget - plausible
- Kinetic energy 315 J, z=1.94 above the 5 kg overhand-throw reference - strained

The acceleration is the decisive demand in this phase: Andrew must drag Victoria from rest to 3.0 m/s in 0.5 s (the first half of the triangular profile), then decelerate her over the second 0.5 s. The 420 N force on Victoria's torso is within the two-arm push budget, but for the force to actually produce 6.0 m/s^2 acceleration of Victoria's mass requires that her feet do not exert opposing friction. Adult shoe-on-tile static friction at mu = 0.3 gives a 206 N opposing-force cap at Victoria's feet, plus the active braking effort of any unwilling subject. The combined demand on Andrew is therefore conservatively underestimated by treating Victoria as a free CoM.

**Phase 2 - Swap+throw (1.0 s, Victoria 0.5 m + 180 deg rotation).** Four scored quantities:

- Peak acceleration 2.0 m/s^2, z=-1.25 - plausible
- Peak force 140 N, z=-3.3 - plausible
- Kinetic energy 35 J, z=-1.56 - plausible
- Peak yaw angular velocity 6.28 rad/s (360 deg/s), z=2.78 above the standing-pivot reference - **implausible**

The linear demands are mild because the translation distance is small. The rotation demand is where the phase breaks. Victoria must complete a 180 deg yaw in 1.0 s, peaking at 6.28 rad/s (twice the population-mean voluntary pivot rate). For a passive subject this rotation must be imposed externally - by Andrew's arms while simultaneously translating Victoria's CoM 0.5 m forward to the impact and managing the swap of his own lateral position.

**Phase 3 - Swap-back (1.0 s, Andrew 180 deg + Victoria 180 deg + position swap).** One scored quantity:

- Peak yaw angular velocity 6.28 rad/s for Andrew's voluntary 180 deg pivot, z=2.78 - **implausible**

Victoria's 180 deg rotation in this phase tracks Andrew as he moves to her right; same 6.28 rad/s peak and same implausible verdict. Andrew's pivot is voluntary (he is the actor) but at 6.28 rad/s it is still ~1.8x the population mean.

![Per-phase demand](figures/01-per-phase-demand.png)

## Time-series kinematics

![Speed timeline](figures/01-speed-timeline.png)
![Acceleration timeline](figures/01-acceleration-timeline.png)
![Force timeline](figures/01-force-timeline.png)
![Cumulative impulse](figures/01-impulse-timeline.png)

The time-series make the structure of the verdict visible. Victoria's acceleration is constant at 6.0 m/s^2 across the pull phase (visible above the elite-sprint reference line) and drops to 2.0 m/s^2 during the swap-throw. Force on Victoria peaks at 420 N during the pull, well below the 800 N two-arm reference. Cumulative impulse delivered to Victoria reaches 280 N s over the pull + swap-throw phases combined. The rotation demand does not appear in these linear-quantity plots; it shows up only in the yaw kinematics summarised in the per-phase table above.

![Reference overlay](figures/01-reference-overlay.png)
![Verdict summary](figures/01-verdict-summary.png)

## Verdict tally

- plausible: 5 of 8 scored demands (pull force, swap-throw acceleration, swap-throw force, swap-throw kinetic energy, and the linear demands within each phase that are sub-population-mean)
- strained: 1 (pull kinetic energy at z=1.94)
- implausible: 2 (swap-throw rotation at z=2.78, swap-back rotation at z=2.78)
- extreme (z > 3): 1 (pull acceleration at z=3.75)

## Overall verdict

The 3-phase reconstruction produces a mixed verdict. Compared to the earlier 2-phase reading (where pull and swap-throw were merged into a single 1.5 s window), splitting the actions into three discrete 1.0 s phases raises the pull-phase acceleration into the extreme band and both rotation rates into the implausible band. This is intrinsic: with the same total displacement budget but compressed into shorter sub-phases, the per-phase peak demands must scale up to deliver the same total motion.

The 3-phase decomposition is the more faithful reconstruction of the verbatim action sequence (pull, swap and throw, swap back). The 2-phase reading was a charitable mathematical simplification that merged two distinct described actions. The 3-phase verdict therefore better reflects what the alleged motion would actually require.

Confidence: medium-high. The 3-phase decomposition follows the user's stated action sequence directly. The pull-phase acceleration of 6 m/s^2 (0.61 g) imposed on an unanchored 70 kg subject is biomechanically anomalous - it sits above the recreational sprint reference and reaches into the elite-sprinter band, even though Victoria is allegedly passive and being pulled by upper-limb contact rather than producing her own ground-reaction force. The two rotation rates at 6.28 rad/s are at the upper edge of the standing-pivot reference distribution.

## What this analysis does not establish

- Whether the alleged motion actually occurred (only kinematic plausibility under the 3-phase reading)
- Whether Andrew's grip and arm trajectory can deliver 420 N to Victoria's torso for 1 s while he himself is decelerating backward through the corridor (only CoM kinematics analysed)
- Whether the impact at the elevator door is consistent with reported injuries (covered separately in `docs/impact_analysis.md`)
- Whether Victoria's feet can be made to slide rather than pivot to absorb the rotation, or whether they remain anchored (rotation reference is for voluntary self-pivot, not arm-imposed rotation)

## Limitations

- Constant-acceleration (triangular velocity) profile per phase is the most charitable interpretation; any departure compresses the effective phase time and pushes peaks higher
- The yaw rotation reference is for voluntary standing pivot of one's own body. Imposing rotation on a passive second body through arm contact has no direct population-data analogue
- Reference distributions are modelled normal with adult-male means and standard deviations. The throw kinetic-energy reference (5 kg-object overhand throw) is the closest available analogue but is not a direct comparator for a 70 kg subject
- The analysis is a population-level kinematic plausibility study against published biomechanics, not a forensic reconstruction of a specific event

## Simulation outputs

- `reports/figures/01-corridor-sim-passive.mp4` - PyBullet animation of the 3-phase trajectory with rigid capsule mannequins (~270 frames, 60 fps, ~4.5 s total). The first 3.0 s is the scored 3-phase window; the trailing 1.5 s is a decorative disengagement (V crouches and slides back through the apartment doorway) and is **not** counted in any kinematic phase or score
- `reports/figures/01-corridor-sim-small.mp4` - identical trajectory with the small-resistance cooperation model in the analytical track
- `reports/01-phase-kinematics.csv` - per-phase peak velocity, acceleration, force, impulse, kinetic energy, angular kinematics for both cooperation models
- `reports/01-phase-scores.csv` - per-(phase, quantity) z-score, multiple-of-mean, verdict band, citation
- `docs/events_reconstruction.md` - narrative event reconstruction
- `docs/impact_analysis.md` - impact-force analysis at the elevator door
