# Corridor Two-Body Plausibility Verdict

## Overview

A minimal 2-phase analytical decomposition of the contested 3-second corridor sequence finds that four of five scored kinematic demands fall in the plausible band against adult-male biomechanical references, and one demand falls in the extreme band: Victoria's required body yaw angular velocity of 8.4 rad/s (~480 deg/s) during the pull-throw, which is 4.9 standard deviations above the population mean for a voluntary standing 180 deg pivot. Force, acceleration and energy are all within human range when the throw is granted the full 1.5 s window. The decisive remaining constraint is biomechanical: the same arms cannot deliver a 2 m linear push AND impose a 360 deg rotation on a passive 70 kg body in 1.5 s.

## Scenario configuration

Geometry maps directly to the corridor layout shared by the user:

```
t = 0.0 s    |V .. A|       initial (V at apartment door, A near elevator)
t = 1.5 s    | .. AV *|     after pull-throw (V impacts elevator; * = impact)
t = 3.0 s    | .. VA |      after reverse (A at elevator with back to door)
```

- Corridor width (apartment door to elevator door) 2.0 m, lateral 1.5 m
- Andrew 90 kg standing 1.80 m, initial position x=1.7 m (near elevator)
- Victoria 70 kg standing 1.68 m, initial position x=0.1 m (apartment doorway)
- 'Pull' and 'swap-and-throw' are explicitly described as mixed actions in the framing, so they collapse into a single 'pull-throw' phase. The 'reverse' is a separate action that swaps positions and rotates Andrew

Two phases:

- **Pull-throw** 1.5 s. Victoria translates 2.0 m from apartment door to elevator door + rotates 360 deg total angular distance (first 180 deg so her back impacts the elevator door; then another 180 deg so she faces Andrew again)
- **Reverse** 1.5 s. Andrew rotates 180 deg; A and V swap positions so Andrew ends at the elevator door with his back to it

Each phase gets half the 3 s budget, which is the most charitable allocation for the actor and minimises the required peak demands.

![Corridor geometry](figures/01-corridor-geometry.png)

![Phase timeline](figures/01-phase-timeline.png)

## Phase-by-phase verdict

**Phase 1 - Pull-throw (1.5 s, Victoria 2.0 m + 360 deg).** Four scored quantities:

- Linear acceleration 3.6 m/s^2 (0.36 g), z=0.7 above the recreational sprint reference - **plausible**
- Peak applied force 249 N, z=-2.8 below the two-arm push budget - **plausible** (comfortably within reach)
- Kinetic energy 249 J delivered to a 70 kg body, z=1.1 above the 5 kg overhand-throw reference of 160 +/- 80 J - **strained**
- Peak yaw angular velocity 8.4 rad/s (~480 deg/s) for Victoria's two consecutive 180 deg rotations, z=4.9 above the standing-pivot reference of 3.5 +/- 1.0 rad/s - **extreme**

The force and acceleration are within ordinary adult-male range when the throw is granted the full 1.5 s window. The energy is on the edge - higher than the typical overhand-throw budget for a 5 kg object but within 1-2 sigma of it. The decisive incongruity is the rotation rate: 480 deg/s peak yaw is 4.9 sigma above the population mean for a voluntary standing pivot, and the population mean already requires coordinated foot positioning and stretch-shortening cycle activation. Imposing this rotation rate on a passive 70 kg subject through arm contact alone has no biomechanical precedent in the cited literature.

**Phase 2 - Reverse (1.5 s, Andrew 180 deg).** One scored quantity:

- Peak yaw angular velocity 4.2 rad/s (~240 deg/s) for Andrew's 180 deg standing pivot, z=0.7 above the standing-pivot reference - **plausible**

Andrew pivoting himself 180 deg in 1.5 s is unremarkable. The simultaneous position swap with Victoria requires only modest lateral motion across the corridor width.

![Per-phase demand](figures/01-per-phase-demand.png)

## Time-series kinematics

![Speed timeline](figures/01-speed-timeline.png)
![Acceleration timeline](figures/01-acceleration-timeline.png)
![Force timeline](figures/01-force-timeline.png)
![Cumulative impulse](figures/01-impulse-timeline.png)

The time-series make the structure of the verdict transparent. Linear demands (speed, acceleration, force) on Victoria sit comfortably below the recreational-sprint and two-arm-push reference lines. Cumulative impulse delivered to Victoria reaches 187 N s over the throw window, well within the impulse a sustained two-arm push can produce. The plot that would visualise the rotation demand is implicit in the kinematic table: 8.4 rad/s peak omega is 2.4x the population mean and 1.6x the elite reference, sustained for 1.5 s.

![Reference overlay](figures/01-reference-overlay.png)
![Verdict summary](figures/01-verdict-summary.png)

## Verdict tally

- plausible: 3 of 5 scored demands (pull-throw acceleration, pull-throw force, reverse yaw angular velocity)
- strained: 1 (pull-throw kinetic energy)
- implausible: 0
- extreme (z > 3): 1 (pull-throw yaw angular velocity)

## Overall verdict

The 2-phase reconstruction of the alleged 3-second motion is **internally inconsistent** in a single specific respect: Victoria's required body rotation rate during the pull-throw exceeds the population biomechanical reference by 4.9 standard deviations. Everything else - the linear push force, the acceleration of a 70 kg body across the corridor, the kinetic energy delivered, Andrew's own 180 deg pivot - sits in plausible or near-plausible territory once the 1.5 s window is granted to each phase.

The decisive question therefore reduces to: can the same arms that translate a 70 kg body 2 m in 1.5 s also impose 360 deg of yaw rotation on that body in the same window? The cited biomechanical references describe voluntary self-pivots of cooperating subjects; imposing rotation on a passive second body through arm contact alone is not documented in the population data because the action has no normal-life analogue. A standing-pivot peak of 8.4 rad/s would have to be imparted without the subject's own foot torque, against the floor friction acting on her feet, while the actor is also delivering a 2 m linear translation through the same upper-limb chain. No mechanism in the cited references supports this combination.

Confidence: medium-high. The 2-phase decomposition is the most charitable mapping of the claim - it grants each described action the maximum duration the 3 s budget allows, minimising required peaks. The conclusion is therefore robust to small variations in phase timing. Compressing either phase tightens the verdict; stretching the total time beyond 3 s relaxes the linear demands but does not resolve the rotation problem until the total budget passes ~6 s.

## Limitations

- Constant-acceleration (triangular velocity) profile per phase is the most charitable interpretation; any departure (e.g. an initial dwell time before the throw begins) compresses the effective phase time and increases the required peaks.
- The yaw rotation reference is for a voluntary standing pivot of one's own body, which has no direct analogue for imposing rotation on a second body. The 4.9 sigma figure is therefore a population-relative bound on what *self*-rotation rates an adult can produce; rotation rates imposed on a passive subject through arm contact would be limited by additional factors (grip mechanics, foot friction on the passive subject) not captured in this reference.
- Reference distributions are modelled normal with adult-male means and standard deviations. The throw kinetic-energy reference is taken from 5 kg-object throws because direct references for throwing 70 kg bodies do not exist in the literature.
- The analysis is a population-level kinematic plausibility study against published biomechanics, not a forensic reconstruction of a specific event. It does not establish what actually happened, only what the described motion would have required in physical terms.

## Simulation outputs

- `reports/figures/01-corridor-sim-passive.mp4` - PyBullet animation of the 2-phase trajectory with rigid capsule mannequins (180 frames, 60 fps)
- `reports/figures/01-corridor-sim-small.mp4` - same trajectory with the small-resistance cooperation model in the analytical track
- `reports/01-phase-kinematics.csv` - per-phase peak velocity, acceleration, force, impulse, kinetic energy, angular kinematics for both cooperation models
- `reports/01-phase-scores.csv` - per-(phase, quantity) z-score, multiple-of-mean, verdict band, citation
