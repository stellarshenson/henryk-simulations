# Corridor Two-Body Plausibility Verdict

## Overview

A minimal 2-phase analytical decomposition of the contested 3-second corridor sequence, using the corrected motion interpretation (Andrew pulling Victoria backward toward the elevator, Victoria's facing direction tracking Andrew throughout), finds that all five scored kinematic demands fall in the plausible or strained band against adult-male biomechanical references. The most stretched single quantity is the throw kinetic energy at 249 J (z=1.1 above the 5 kg overhand-throw reference of 160 ± 80 J), which is strained but within population variance. The motion as described in the corrected reading is biomechanically achievable.

## Scenario configuration

Geometry maps to the corridor layout provided as ASCII:

```
pre-timer    |V A .. |       (A has approached V; both near apartment door)
t = 0.0 s    |V A .. |       (timer starts)
t = 1.5 s    | .. AV*|       (A moves backward to elevator pulling V across,
                              V impacts elevator at the swap; * = impact)
t = 3.0 s    | .. VA |       (positions swap back; A at elevator with back to it)
```

- Corridor width (apartment door to elevator door) 2.0 m, lateral 1.5 m
- Andrew 90 kg standing 1.80 m, initial position x=0.5 m (just inside the corridor, in front of V)
- Victoria 70 kg standing 1.68 m, initial position x=0.1 m (apartment doorway)
- Both face the elevator initially (+x). Victoria's facing direction rotates to track Andrew continuously - she always looks at him
- The pull and swap-and-throw are explicitly mixed in the framing, so they collapse into a single 1.5 s 'pull-throw' phase. Reverse is a separate 1.5 s phase

Two phases:

- **Pull-throw** 1.5 s. Andrew moves backward from x=0.5 to x=1.7 toward the elevator while pulling Victoria from x=0.1 to x=2.0. Positions effectively swap during the motion - Victoria overtakes Andrew and ends pinned at the elevator door. Victoria rotates 180 deg as Andrew transitions from in front of her to behind her
- **Reverse** 1.5 s. Andrew rotates 180 deg and moves to the elevator door (ends with back to it); Victoria moves left from x=2.0 to x=1.5 and rotates another 180 deg to continue facing Andrew

Each phase gets half the 3 s budget, the most charitable allocation. The pull and throw motions are merged into one continuous 1.5 s window which minimises required peak acceleration and velocity.

![Corridor geometry](figures/01-corridor-geometry.png)

![Phase timeline](figures/01-phase-timeline.png)

## Phase-by-phase verdict

**Phase 1 - Pull-throw (1.5 s, Victoria 2.0 m + 180 deg rotation).** Four scored quantities:

- Linear acceleration 3.6 m/s^2 (0.36 g), z=0.7 above the recreational sprint reference - **plausible**
- Peak applied force 249 N, z=-2.8 below the two-arm push budget - **plausible** (well within reach)
- Kinetic energy 249 J delivered to a 70 kg body, z=1.1 above the 5 kg overhand-throw reference - **strained**
- Peak yaw angular velocity 4.2 rad/s (~240 deg/s) for Victoria's 180 deg rotation tracking Andrew, z=0.7 above the standing-pivot reference - **plausible**

Note: the kinetic energy is in the strained band because the 5 kg overhand-throw reference is for a much smaller object. The energy budget is dictated by the impulse-momentum relation: 249 N applied for 1.5 s yields 374 N s of impulse and a release velocity of 2.7 m/s, which carries 249 J of kinetic energy into the 70 kg body. The actor must absorb the reaction impulse through stance and grip.

**Phase 2 - Reverse (1.5 s, Andrew 180 deg + Victoria 180 deg + position swap).** One scored quantity:

- Peak yaw angular velocity 4.2 rad/s for Andrew's 180 deg pivot, z=0.7 above the standing-pivot reference - **plausible**

Victoria's 180 deg rotation in this phase (tracking Andrew as he moves to her right) has the same peak rate of 4.2 rad/s and the same plausible verdict. The position swap involves a 0.5 m lateral motion for Victoria and a 0.3 m motion for Andrew, both modest.

![Per-phase demand](figures/01-per-phase-demand.png)

## Time-series kinematics

![Speed timeline](figures/01-speed-timeline.png)
![Acceleration timeline](figures/01-acceleration-timeline.png)
![Force timeline](figures/01-force-timeline.png)
![Cumulative impulse](figures/01-impulse-timeline.png)

The time-series make the plausibility transparent. Victoria's peak speed of 2.7 m/s is brisk-walk pace; her peak acceleration of 3.6 m/s^2 sits right around the recreational sprint reference; the force on her torso of 249 N is well below the 400 N single-arm push budget. Cumulative impulse reaches 374 N s over the throw window - delivered by a sustained two-arm grip well within the population range.

![Reference overlay](figures/01-reference-overlay.png)
![Verdict summary](figures/01-verdict-summary.png)

## Verdict tally

- plausible: 4 of 5 scored demands (pull-throw acceleration, pull-throw force, pull-throw rotation, reverse rotation)
- strained: 1 (pull-throw kinetic energy)
- implausible: 0
- extreme (z > 3): 0

## Overall verdict

Under the corrected motion interpretation (pull and throw mixed into a single 1.5 s window, Victoria's body rotation distributed evenly across both phases tracking Andrew's relative bearing), the alleged 3-second motion is **physically achievable**. Every scored kinematic demand sits within population biomechanical reference distributions, with the kinetic energy being the most stretched single quantity at z=1.1 (strained but not extreme).

This represents an important conclusion: the kinematic feasibility of the alleged motion depends sensitively on the assumed motion decomposition. Earlier interpretations (more sub-phases, all rotation concentrated in the throw, V crossing the corridor toward a stationary A) produced extreme verdicts in the throw kinematics. The corrected reading - which compresses the actions into the minimum number of phases, gives the actor maximum time per action, and distributes V's rotation across both phases - produces a plausible verdict.

Confidence: medium. The 2-phase decomposition is the most charitable mapping of the claim. The conclusion is therefore a *necessary* but not *sufficient* condition for the alleged motion: physical possibility does not establish that the motion occurred. The analysis only shows that the kinematic demands of the alleged motion, under the most favourable interpretation, sit within population biomechanical ranges.

## What this analysis does not establish

- Whether the alleged motion actually occurred (only physical possibility)
- Whether grip mechanics, joint kinematics or stance permit the specific arm trajectories required to apply the impulse (only torso-CoM and yaw kinematics analysed)
- Whether the impact-force on Victoria's back at the elevator door is consistent with described injuries (only translational kinetic energy analysed)
- Whether a 70 kg passive subject can be pulled 2 m by a 90 kg actor without sliding feet, balance loss, or other coupling effects not captured in a CoM model
- The role of static friction between Victoria's feet and the floor in resisting the pull (could increase required force, but the analysis already shows force is comfortably below the budget)

## Limitations

- Constant-acceleration (triangular velocity) profile per phase is the most charitable interpretation; any departure compresses the effective phase time and increases the required peaks.
- The yaw rotation reference is for voluntary standing pivot of one's own body. Imposing rotation on a passive second body through arm contact has no direct population-data analogue; the 4.2 rad/s figure is therefore a *lower bound* on what arm-imposed rotation rates can be sustained, not a measured population mean for that specific action.
- Reference distributions are normal with adult-male means and standard deviations. The throw kinetic-energy reference (5 kg-object overhand throw) is the closest available analogue but is not a direct comparator for projecting a 70 kg passive subject.
- The analysis is a population-level kinematic plausibility study against published biomechanics, not a forensic reconstruction of a specific event.

## Simulation outputs

- `reports/figures/01-corridor-sim-passive.mp4` - PyBullet animation of the 2-phase trajectory with rigid capsule mannequins (181 frames, 60 fps): both start at the apartment door, A pulls V backward toward the elevator, V impacts the elevator at the swap, positions reverse with A ending at the elevator with back to it
- `reports/figures/01-corridor-sim-small.mp4` - identical trajectory with the small-resistance cooperation model in the analytical track
- `reports/01-phase-kinematics.csv` - per-phase peak velocity, acceleration, force, impulse, kinetic energy, angular kinematics for both cooperation models
- `reports/01-phase-scores.csv` - per-(phase, quantity) z-score, multiple-of-mean, verdict band, citation
