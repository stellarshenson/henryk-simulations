# Events Reconstruction - 3-Phase Corridor Sequence

## Scenario

The contested 3-second sequence in a 2 m corridor is decomposed into three discrete actions, each receiving a 1.0 s share of the total time budget. This is the minimum-phase decomposition that maps the claim onto separable physical motions while keeping the actor maximally charitable on time per action. The cooperation model is **passive worst-case**: Victoria is treated as a fully passive 70 kg body with no resistive friction or grip from her end. Adding any resistance only increases the actor's required force, so the passive model is a lower bound on the demand.

The corridor topology, with V = Victoria, A = Andrew:

```
pre-timer    |V A .. |       A has approached V; both stand near the apartment door
t = 0.0 s    |V A .. |       timer starts
t = 1.0 s    | .. VA |       after pull
t = 2.0 s    | .. AV*|       after swap+throw; V's back impacts elevator door (*)
t = 3.0 s    | .. VA |       after swap-back; A ends at elevator with back to it, V 40 cm in front of A
```

Initial positions: V at x=0.14 m (apartment doorway, back surface clearing the wall), A at x=0.50 m (just inside the corridor, in front of V). Both face toward the elevator at +x. V's facing direction tracks A's relative bearing - she rotates 180° each time positions swap.

## Phase 1 - Pull (1.0 s)

Andrew retreats backward toward the elevator while pulling Victoria along. Victoria translates 1.5 m from x=0.14 to x=1.64. Andrew retreats from x=0.50 to x=1.64, keeping V slightly behind. No rotation in this phase.

Velocity profile: V accelerates uniformly from rest. By construction, the end-of-phase velocity carries through into phase 2.

| Quantity | Value |
|---|---|
| duration | 1.00 s |
| V displacement | 1.5 m |
| v_start | 0.0 m/s |
| v_end | 3.0 m/s (10.8 km/h) |
| a_avg (constant accel) | +3.00 m/s² (0.31 g) |
| F_avg on V | 210 N |
| impulse delivered | +210 N·s |
| KE_start | 0 J |
| KE_end | 315 J |
| work done on V | +315 J |
| **a_peak (triangular profile)** | **6.00 m/s² (0.61 g)** |
| **F_peak (triangular profile)** | **420 N** |

Two kinematic models are reported because the velocity profile is not directly observable from the claim:

- **Constant acceleration** (continuous-velocity): V accelerates uniformly through the pull and carries the 3.0 m/s into the impact. Average force 210 N, peak force 210 N.
- **Triangular profile** (peaks): V accelerates for the first half then decelerates back to rest by end-of-phase. Peak force 420 N at the midpoint. This model is conservative for actor effort (higher peak demand) but inconsistent with V's velocity continuity into phase 2.

The constant-acceleration model is the one used by the impact analysis (it produces the realistic 3.0 m/s impact velocity at end of phase 2).

Verdicts:

- peak acceleration (triangular) 6.0 m/s² vs recreational sprint 3.0 ± 0.8: z = 3.75 → **extreme**
- average acceleration 3.0 m/s² vs same reference: z = 0.0 → plausible (this is what the actor must actually sustain)
- peak force 420 N vs two-arm push 800 ± 200: z = -1.9 → plausible
- kinetic energy delivered 315 J vs 5 kg overhand throw 160 ± 80: z = 1.94 → strained

## Phase 2 - Swap and throw + impact (1.0 s)

Positions exchange. Andrew swaps from V's front to V's back, moving from x=1.64 to x=1.50. Victoria's CoM advances 0.22 m further (from x=1.64 to x=1.86) so her back surface contacts the elevator door at x=2.0. Victoria rotates 180° during the swap to keep facing Andrew. The impact happens at the end of the phase.

| Quantity | Value |
|---|---|
| duration | 1.00 s |
| V translation distance | 0.22 m |
| v_start (carried from pull) | 3.0 m/s |
| v_end (post-impact, at rest) | 0.0 m/s |
| Δv | -3.0 m/s |
| a_avg | -3.00 m/s² |
| impulse_net | -210 N·s |
| KE delivered into the wall | 315 J |
| V rotation | 180° (π rad) |
| ω_peak (triangular) | 6.28 rad/s (360°/s) |
| τ_peak | 17.6 N·m |
| rotational KE | 27.6 J |

### Impact at the elevator door

The impact happens when Victoria's CoM reaches x=1.86 (her back touches the wall at x=2.0). The deceleration is modelled as constant over the **2.0 cm stopping distance** (configurable as `STOPPING_DISTANCE_CM` in the notebook), which combines tissue compression, door panel flex, and small body travel.

| Quantity | Value |
|---|---|
| v_impact | 3.00 m/s (10.8 km/h) |
| stopping distance | 2.0 cm |
| KE_impact | 315 J |
| momentum | 210 N·s |
| a_impact | 225 m/s² = **22.9 g** |
| **F_impact** | **15.75 kN** |
| t_stop | 13.3 ms |

15.75 kN is well within the documented range for thoracic-wall impacts that produce rib fractures in the biomechanics literature (see `docs/impact_analysis.md`). A 2-cm stopping distance is a generous estimate; tighter coupling (1 cm) doubles the peak force to ~31 kN.

Verdicts:

- linear translation kinematics (peak a 0.88 m/s², F 62 N, KE 7 J): all plausible
- peak yaw angular velocity 6.28 rad/s vs standing pivot 3.5 ± 1.0: z = 2.78 → **implausible**

## Phase 3 - Swap back (1.0 s)

Positions exchange again. Andrew advances to the elevator door (x=1.50 → x=1.86) and rotates 180° so his back faces the elevator. Victoria steps back 40 cm (x=1.86 → x=1.46) and rotates another 180° to keep facing Andrew. The end state has Victoria standing approximately 40 cm in front of Andrew - this is the configuration the witness later sees.

**Andrew (primary)**:

| Quantity | Value |
|---|---|
| duration | 1.00 s |
| translation (CoM) | 0.36 m |
| rotation | 180° |
| ω_peak | 6.28 rad/s (360°/s) |
| τ_peak | 22.6 N·m |
| rotational KE | 35.5 J |

**Victoria (secondary - step-back + rotation)**:

| Quantity | Value |
|---|---|
| duration | 1.00 s |
| translation | 0.40 m |
| v_peak (triangular) | 0.80 m/s |
| a_peak (triangular) | 1.60 m/s² (0.16 g) |
| F_peak | 112 N |
| KE_peak | 22.4 J |
| rotation | 180° |
| ω_peak | 6.28 rad/s (360°/s) |
| τ_peak | 17.6 N·m |
| rotational KE | 27.6 J |

V's step-back is the smallest motion in the whole sequence. The dominant demand in phase 3 is the rotation rate - 360°/s applied to both bodies in 1.0 s.

Verdicts:

- A's peak yaw angular velocity 6.28 rad/s, z = 2.78 → **implausible**
- V's peak yaw angular velocity 6.28 rad/s, z = 2.78 → **implausible**
- V's translation (force 112 N, KE 22 J): plausible

## Post-event disengagement (visual only, NOT a scored phase)

After the 3 s contested window, the MP4 renders an additional ~1.5 s of decorative aftermath: Victoria crouches forward and slides back through the (translucent) apartment doorway, exiting the corridor. Andrew remains at the elevator door with his back to it. This trailing animation is rendering-only - it is **not** added to the Scenario's phase list, does not appear in the kinematic tables, and does not contribute to any plausibility score. It is included because the verbatim claim ends with "and then she fell"; depicting that aftermath in the same clip makes the timeline more readable. The full MP4 therefore runs ~4.5 s while the kinematic analysis covers only the first 3.0 s.

## Aggregate verdict

| Phase | Demand | Value | z | Verdict |
|---|---|---|---|---|
| pull | peak acceleration | 6.00 m/s² (0.61 g) | 3.75 | **extreme** |
| pull | peak force | 420 N | -1.90 | plausible |
| pull | kinetic energy | 315 J | 1.94 | strained |
| swap-throw | peak acceleration | 0.88 m/s² | -2.65 | plausible |
| swap-throw | peak force | 62 N | -3.69 | plausible |
| swap-throw | kinetic energy at v_peak | 7 J | -1.91 | plausible |
| swap-throw | yaw angular velocity | 6.28 rad/s (360°/s) | 2.78 | **implausible** |
| swap-throw | **F_impact at wall** | **15.75 kN** | n/a | rib-fracture range |
| swap-back (A) | yaw angular velocity | 6.28 rad/s | 2.78 | **implausible** |
| swap-back (V) | yaw angular velocity | 6.28 rad/s | 2.78 | **implausible** |
| swap-back (V) | translation peak force | 112 N | -3.44 | plausible |

The decisive findings are concentrated in:

- **Phase 1 acceleration** at z=3.75 (triangular peak interpretation; the average-acceleration interpretation under constant-accel sits at z=0). The peak demand is a tooling artefact of the triangular profile - if Andrew applies a *constant* 210 N pull throughout the second, the demand stays at the recreational-sprint mean.
- **All three rotation rates** at z=2.78 (360°/s yaw imposed in 1.0 s windows). A's own rotation is voluntary but at twice the population-mean pivot rate; V's two rotations are imposed by Andrew's arm contact while she is also being translated and impacted, with no biomechanical precedent in the cited literature.
- **Impact force 15.75 kN** at the elevator door is in the rib-fracture range documented by the experimental thoracic-impact literature (see `docs/impact_analysis.md` for citations).

## What this analysis does not establish

- Whether the alleged motion actually occurred (only kinematic plausibility under the most charitable cooperation model)
- Whether Andrew's grip and arm trajectory can deliver 210 N to Victoria's torso for 1 s while he himself is decelerating backward through the corridor (only CoM kinematics analysed)
- Whether the actual injury pattern (single bruise vs widespread thoracic trauma) is consistent with the 15.75 kN impact force (this is the question `docs/impact_analysis.md` addresses)
- Whether Victoria's feet slide or remain anchored during the pull (rotation reference is for voluntary self-pivot, not arm-imposed rotation)

## See also

- `reports/corridor-plausibility.md` - full plausibility report with figures and reference citations
- `reports/figures/01-corridor-sim-passive.mp4` - PyBullet animation of the 3-phase trajectory + disengagement
- `reports/figures/01-phase-timeline.png` - phase Gantt chart
- `reports/figures/01-verdict-summary.png` - z-score lollipop summary
- `reports/figures/01-acceleration-timeline.png`, `01-force-timeline.png`, `01-speed-timeline.png`, `01-impulse-timeline.png` - per-body time series
- `docs/impact_analysis.md` - impact-force analysis at the elevator door (Polish)
- `references/biomechanics-sources.md` - bibliography for the reference distributions
- `references/pictures/` - reference photos of the corridor geometry (EXIF/GPS stripped)
