# henryk-simulations

[![Build](https://github.com/stellarshenson/henryk-simulations/actions/workflows/build.yml/badge.svg)](https://github.com/stellarshenson/henryk-simulations/actions/workflows/build.yml)
[![Donate PayPal](https://img.shields.io/badge/Donate-PayPal-blue?style=flat)](https://www.paypal.com/donate/?hosted_button_id=B4KPBJDLLXTSA)

Numerical and physics-based reconstructions of contested real-world events. Built to disclose the role of forces, accelerations, momenta and biomechanical limits in things people claim happened in three seconds.

Current scene: **Mk1 - Corridor Attack Incident Reconstruction**.

Most people, when falsely accused, hire a lawyer and wait. I wrote a physics simulation.

![Most people hire a lawyer. I wrote a physics simulation.](docs/medium/images/07-physics-vs-litigation.svg)

> [!IMPORTANT]
> The event as described by the victim **did not happen**. The father is currently using science, physics, simulation, geometry and statistics to prove to the half-witted court officials that the laws of physics would have to take an unscheduled coffee break for the events to unfold the way the victim portrayed them.
>
> The father and his son are the victims of **parental alienation**. The fabricated incident is one instrument in that wider pattern; the physics-based reconstruction in this repo is one of the means the father is using to push back against it.

> [!NOTE]
> This project serves an **educational purpose**. All names of the actors have been changed so that no one involved in the underlying matter is endangered or identifiable from the repository.

[![Corridor Attack Incident Reconstruction Mk1](https://i.ytimg.com/vi/V-ooOpqg4aU/hqdefault.jpg)](https://www.youtube.com/watch?v=V-ooOpqg4aU)

> Click the thumbnail for the rendered simulation on YouTube.

> [!TIP]
> The narrative version of the story is on Medium: **[The 3-second throw that couldn't happen - a legal science story](https://pub.towardsai.net/the-3-second-throw-that-couldnt-happen-a-legal-science-story-8cd705a99fa1)** (Towards AI).

The core trick is to reconstruct the smallest possible motion that still admits the verbatim testimony. If even that lower bound exceeds what a body can do, every richer reading of the accusation exceeds it too.

![Lower-bound argument (ELBO-style)](docs/medium/images/01-lower-bound-argument.svg)

The setup the lower-bound reconstruction runs against: a two-segment corridor with the apartment door on the north wall and the elevator door on the south wall, plus the props and starting positions Victoria, Andrew and Cecilia were in at t=0.

![Corridor overhead geometry](reports/figures/01-corridor-geometry.png)

> Overhead corridor geometry used by the reconstruction: two-segment W-to-E layout with the S-side elevator-door elbow, apt door swinging W into segment 2, and the setup positions of Victoria (V) inside the apt-door envelope, Andrew (A) pressed flat against the elevator door, and Cecilia (C) in segment 1. [Box] is the 50x30 cm aluminium briefcase at the E edge of the elevator door; [Str] is the stroller in the NW corner of segment 2.

## What this is

The accusation is specific: three seconds in a corridor. The father was supposed to have pulled the alleged victim back, swapped places with her, thrown her back-first into the elevator door, and swapped places again. All of this in front of a court-appointed social curator who, by her own testimony, had her back turned at the precise moment of the alleged impact.

Three seconds. Two doors, two metres apart. A 70 kg adult moving as a rigid object. A 90 kg actor doing the moving.

The father is not a lawyer. He is the kind of person who reaches for `scipy.stats` and `compute_impact()` when faced with an emotional problem. So he built this repo.

At the most charitable possible interpretation of the accusation, the impact would have delivered **18 kilonewtons of peak force**, **26 g of deceleration**, and a peak sound pressure level of **124 dB** at the phone microphone that was recording the entire visit. The medical examination afterwards documented one bruise on the right shoulder. The recording contains neither a clipping spike nor any panel-ringing acoustic signature. The third-party witness reports no loud noise of any kind.

You can decide for yourself what that means. The reconstruction cheats on the prosecution's behalf throughout - the accusation gets the friendliest possible reading - and the accusation still fails the physics.

## What's in here

Four kinds of artefacts bundled together:

- **Forensic record** - corridor topology and dimensions, five chronologically ordered versions of the alleged victim's testimony, the third-party social curator's positional and temporal account, a narrative-escalation log tracking how the story changed across filings, and the EXIF-clean audio recording of the entire visit as the acoustic ground truth
- **Physics library** - per-phase kinematic and dynamic quantities the claim implies (linear and angular velocities, peak accelerations, forces, impulses, kinetic energies, impact force on the elevator door, peak g-loading on the chest); each quantity scored against a published biomechanical reference distribution drawn from Daams, Mital, Mero, Cross, Hodgson, Plagenhoef, Viano, Cavanaugh, Stapp, Eiband, Sturdivan and Kemper, emitting a z-score and a colour-coded verdict band
- **Acoustics module** - Kirchhoff plate equation for the elevator door's flexural modes, half-wave resonance of the air gap between the two steel panels, peak sound pressure predicted at three listener positions including the phone microphone that recorded the visit; cross-checked against the actual audio waveform for the expected clipping spike and panel ringing
- **PyBullet simulation** - rigid-body render of the alleged motion as an MP4 with custom capsule mannequins, plus a dozen matplotlib figures showing per-phase demand bars, force and acceleration timelines, injury-threshold zones, the four-views-of-impact panel, and the audio signature prediction

Every number in the analysis is reproducible by running one notebook against a single nested `PARAMS` dictionary; ruff-clean Python, pytest-covered, managed by `uv`.

## Aim

Stress-test the contested 3 s claim against the laws of physics and against population biomechanical references, using the verbatim testimony, the reconstructed corridor geometry, and the third-party observation as the sole inputs. Specifically:

- Compute every kinematic quantity the claim implies per phase: linear velocity (start, end, peak), linear acceleration (peak), angular velocity, angular acceleration, force, impulse, kinetic energy, torque, angular momentum, impact force and g-loading at the elevator door
- Score each quantity against a published biomechanical reference distribution and emit a z-score plus a verdict band (plausible / strained / implausible)
- Render the reconstruction in PyBullet so the geometry, the swap and the impact are visually inspectable, not just tabular
- Constrain the reconstruction to the **minimum** number of phases that still admits the verbatim claim, so the computed demand is a **lower bound** on the true required demand (the ELBO-style argument in [`references/incident/events_reconstruction.md`](references/incident/events_reconstruction.md))
- Keep all reconstruction inputs (geometry, testimonies, inconsistency log) in version control under [`references/incident/`](references/incident/) so the result is reproducible end-to-end from documents to numbers to video

## Features

### Reconstruction inputs ([`references/incident/`](references/incident/), [`data/external/event_audio/`](data/external/event_audio/))

- [`geometry.md`](references/incident/geometry.md) - corridor topology (W-to-E run, two segments, S-side elbow), dimensions (~2 m N-S width, apt door ~1 m Polish standard), actor setup positions, props ([Box] aluminium briefcase 50x30 cm at the E edge of the elevator door, [Str] stroller in segment 2 NW), apt door swing direction
- [`testimony_victim.md`](references/incident/testimony_victim.md) - five chronologically ordered versions of the victim's account (live audio exclamation, medical examination, October prosecutor filing, December court motion, March restraining-order motion)
- [`testimony_3rd_party.md`](references/incident/testimony_3rd_party.md) - court social curator's positional and temporal observations (asked to step aside, three steps and turned away, what she saw when she turned back)
- [`testimony_victoria_inconsistencies.md`](references/incident/testimony_victoria_inconsistencies.md) - narrative-escalation table across the five tellings
- [`events_reconstruction.md`](references/incident/events_reconstruction.md) - minimum-viable stage decomposition (Setup / Approach / Pull / Swap+Throw / Swap-Again / Disengage), formal ELBO-style lower-bound formulation with LaTeX, side-by-side analogy table with variational inference
- [`data/external/event_audio/event_recording.m4a`](data/external/event_audio/event_recording.m4a) - full audio recording of the visit and the contested moment; the source for both the third-party testimony and the victim's verbatim live exclamation

### Kinematic computations ([`src/henryk_simulations/corridor/`](src/henryk_simulations/corridor/))

- Per-phase: triangular velocity profile (v_peak = 2s/t, a_peak = 4s/t²), continuous-velocity model with carry-over momentum across phases, peak force (F = m·a), impulse (J = m·Δv), kinetic energy (KE = ½mv²), angular velocity, angular acceleration, torque, angular momentum
- Impact analysis: F_impact = m·v²/2d with configurable stopping distance, peak g-loading, post-impact deceleration
- All knobs (per-phase durations, stopping distance, body masses, geometry, resistance model) parameterised via dataclasses in [`config.py`](src/henryk_simulations/corridor/config.py)
- Resistance model: `passive` (worst-case-for-defence: victim as cooperating mass, no resistive force subtracted from the attacker's demand)

### Plausibility scoring ([`plausibility.py`](src/henryk_simulations/corridor/plausibility.py), [`references.py`](src/henryk_simulations/corridor/references.py))

- Population reference distributions as `scipy.stats` objects: single-arm and two-arm peak push force (Daams 1994, Mital 1995), sprint acceleration recreational and elite (Mero 2005), overhand throw kinetic energy (Cross 2004), standing-pivot yaw angular velocity (Hodgson 2008), whole-body yaw moment of inertia (Plagenhoef 1983)
- Per-quantity z-score, percentile, verdict bands at z = 1 (strained), z = 2 (implausible), z = 3 (extreme)

### PyBullet rendering ([`sim.py`](src/henryk_simulations/corridor/sim.py))

- Custom rigid capsule mannequins built from primitives (no URDF ragdoll sprawl)
- Scripted phase motion at 60 Hz: pull, swap+throw, swap-back, plus a non-scored 1.5 s disengagement tail (V crouches and slides back through the apt doorway)
- Impact frame: elevator wall flashes yellow at the impact tick for visual confirmation
- 4.5 s MP4 output (3 s scored + 1.5 s tail), encoded with `imageio[ffmpeg]`, fixed external camera, no GUI window required

### Figures ([`plots.py`](src/henryk_simulations/corridor/plots.py), output to [`reports/figures/`](reports/figures/))

- `01-corridor-geometry.png` - overhead corridor topology with two-segment W-to-E layout, S-elbow, apt door swing, actor setup positions (V, A, C), [Box] briefcase, [Str] stroller
- `01-phase-timeline.png` - gantt of the three scored phases over the 3 s budget
- `01-speed-timeline.png`, `01-acceleration-timeline.png`, `01-force-timeline.png`, `01-impulse-timeline.png` - per-actor continuous timelines across the full reconstruction
- `01-per-phase-demand.png` - per-phase bar chart of peak demands
- `01-reference-overlay.png` - reference distribution overlay with the per-phase required value marked, one panel per biomechanical quantity
- `01-verdict-summary.png` - headline plausibility verdict per phase per quantity
- `01-arm-conflict.png` - same-arms conflict figure for the throat-grab variant
- `01-corridor-sim-passive.mp4` - rendered PyBullet simulation

### Analytical notebook ([`notebooks/01-kj-corridor-kinematics.ipynb`](notebooks/01-kj-corridor-kinematics.ipynb))

- Cross-references the incident folder and the methodology section in the header
- Configuration cell with `PHASE_DURATIONS` and `STOPPING_DISTANCE_CM` knobs
- Rich `box.ROUNDED` tables with cyan headers for per-phase deconstruction (continuous-velocity, triangular peaks, rotation, impact)
- All figures generated in-line; CSV tables written to [`reports/01-phase-kinematics.csv`](reports/01-phase-kinematics.csv) and [`reports/01-phase-scores.csv`](reports/01-phase-scores.csv)

### Tabular outputs ([`reports/`](reports/))

- `01-phase-kinematics.csv` - per-phase numerical results
- `01-phase-scores.csv` - per-phase z-scores and verdict bands

## Headline numbers (Mk1, no-resistance / worst case for the defence)

| Stage | v_end | a_peak | ω_peak | Verdict |
|---|---|---|---|---|
| Pull | 3.0 m/s | 6.0 m/s² | - | a_peak extreme (z = 3.75) |
| Swap + throw | 0 (impact) | 2.0 m/s² | 6.28 rad/s | ω implausible (z = 2.78); impact F = 15.75 kN, 22.9 g over 2 cm stopping distance |
| Swap-back | 0 | 2.0 m/s² | 6.28 rad/s | ω implausible (z = 2.78) |

Configurable knobs (phase durations, stopping distance) live in the notebook config cell.

What the lower bound predicts the impact would have produced, set against what the actual medical, acoustic and witness record shows - the gap between the two is the forensic equivalent of a KL divergence between model and reality.

![Lower bound vs documented record - the forensic gap](docs/medium/images/11-elbo-incident.svg)

## Quick start

```bash
make install                                                                                 # uv venv + deps
make test                                                                                    # pytest
make lint                                                                                    # ruff
jupyter nbconvert --to notebook --execute notebooks/01-kj-corridor-kinematics.ipynb --inplace
python -m henryk_simulations.corridor.sim                                                    # render the MP4
```

Outputs land under `reports/figures/` (PNG figures, MP4 simulation) and `reports/` (per-phase CSV tables).

## Repo layout

```
references/incident/                  geometry, testimonies, inconsistency log, methodology
notebooks/01-kj-corridor-kinematics   per-phase kinematics, scoring, plots
src/henryk_simulations/corridor/      config, kinematics, sim (PyBullet), plots
reports/figures/                      generated figures and the MP4
```

Other Makefile targets: `make build`, `make clean`, `make format`, `make help`.

## Methodology in one paragraph

Minimum-phase decomposition with maximum time per phase gives the lowest physically achievable demand. If that lower bound already exceeds population biomechanical references, the true motion exceeds them by at least as much. Any richer reconstruction (throat-grab, defensive grab, left-side approach, strangulation attempt - all of which appear in later filings) compresses each remaining phase, pushes peak accelerations and angular velocities up, and makes the verdict strictly worse for the claim. See [`references/incident/events_reconstruction.md`](references/incident/events_reconstruction.md) for the formal lower-bound argument and the ELBO analogy.

Crash reconstruction asks did this specific impact happen. This test asks the prior question: could this story have happened at all. Four years of contested family-court litigation, substantially clarified by twenty minutes of biomechanics.

## Status

Mk1 is rendered, scored and pushed. Mk2 will refine the impact model and add the same-arms conflict analysis for the late-filing throat-grab variant.

---

> Scaffolded from [copier-data-science](https://github.com/stellarshenson/copier-data-science) v1.3.5.
