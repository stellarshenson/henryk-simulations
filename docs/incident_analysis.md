# Incident Analysis

Forensic reconstruction of the contested 3 s corridor incident. Cross-references the minimum-phase simulation in [`../notebooks/01-kj-corridor-kinematics.ipynb`](../notebooks/01-kj-corridor-kinematics.ipynb), the testimony set under [`../references/incident/`](../references/incident/), the biomechanics literature in [`./biomechanics-sources.md`](./biomechanics-sources.md) and [`./impact_analysis.md`](./impact_analysis.md), and the rendered simulation in [the YouTube reconstruction](https://youtu.be/V-ooOpqg4aU).

## 1. Executive Summary

> [!IMPORTANT]
> The event as described in V's testimony **did not occur as claimed**. This document presents the forensic basis: a lower-bound physics reconstruction whose predicted mechanical, medical, acoustic and observational outcomes are absent from or contradicted by the documented record. Intended for evidentiary use; names anonymised throughout the repository.

**The claim**. V states A pulled her ~1.5 m southward, threw her back-first into the elevator door, then swapped positions again, all within ~3 s.

**The lower-bound physics**. Minimum-phase reconstruction (one phase per claimed action, maximum time per phase) yields the smallest demand any compatible motion can impose. Headline numbers:

- Impact velocity: **3.21 m/s** (11.6 kph)
- Peak deceleration: **26.3 g**
- Peak impact force: **18.06 kN**
- Kinetic energy absorbed: **361 J**
- Impulse delivered: **0.225 kN·s** over 12.5 ms
- Predicted peak SPL at phone microphone (~2 m): **124 dB** (above the ~120 dB consumer-mic clip ceiling)

**Predicted damage band**. AIS 5+ critical / life-threatening thoracic injury (Viano 1989, ref 8); rear-torso experimental literature puts comparable loads at rib fracture + costo-vertebral / costo-transverse joint injuries (refs 14, 15).

**Documented findings**. Single right-shoulder bruise on medical examination; no rib fracture, no breathing complaint, full thoracic mobility, no audio clipping spike, no steel-panel ringing in the recording, no acoustic reaction from the line-of-sight third-party observer (C).

> [!CAUTION]
> **Key conclusion**. Every outcome-side observable predicted by the lower-bound physics is either absent from the documented record or directly contradicted by the third-party witness. The claimed motion is not consistent with the documented evidence across mechanical, medical, acoustic and observational channels simultaneously.

## 2. Incident Overview

- Date: 13 September 2025; corridor at apt door / elevator door, second-floor
- Participants: A (father, 90 kg), V (mother, 70 kg), C (court social curator, witness), child
- Total claimed duration: ~3 s
- V's claim (synthesised): A pulled V south toward elevator, swapped positions, threw V back-first into elevator door, swapped positions again, V slid to floor
- Audio recording active throughout (`../data/external/event_audio/event_recording.m4a`)

## 3. Geometry

Source: [`../references/incident/geometry.md`](../references/incident/geometry.md).

- Corridor runs W to E in two segments; segment 1 entry-narrow, segment 2 wider, holds both doors
- Apt door on N wall of segment 2, ~1 m wide (Polish standard), opens W into corridor
- Elevator door on S wall of segment 2, 2 m × 1 m, two 2 mm steel plates with 3 cm air gap, 20 × 60 cm glass window
- N-S throw distance apt-door to elevator-door: **~2 m**
- A at setup: back pressed flat against elevator door (max retreat), facing N
- V at setup: inside apt-door envelope on W side, facing S
- C at setup: segment 1, facing E, line-of-sight to segment 2
- Props: aluminium briefcase 50 × 30 cm at E edge of elevator door (`[Box]`), stroller in NW corner of segment 2 (`[Str]`)

![Corridor overhead geometry](../reports/figures/01-corridor-geometry.png)

## 4. Testimonials

Sources: [`testimony_victim.md`](../references/incident/testimony_victim.md), [`testimony_3rd_party.md`](../references/incident/testimony_3rd_party.md), [`testimony_victoria_inconsistencies.md`](../references/incident/testimony_victoria_inconsistencies.md).

V's account escalates across five chronological retellings:

| # | Date | Source | Added element |
|---|---|---|---|
| 1 | 2025-09-13 | live audio | "threw himself at me at the neck" |
| 2 | 2025-09-13 | medical exam | pushed against elevator, back-first |
| 3 | 2025-10 | pismo to prosecutor | "threw himself and pushed" |
| 4 | 2025-12 | court motion | + throat-grab + defensive grab |
| 5 | 2026-03 | restraining-order motion | + attempted strangulation + left-side approach |

C's observation (segment 1, line-of-sight): asked to step aside, took three steps, turned away briefly, on turning back observed V leaning against A front-first with A's hands raised, V slid down door front-first then crawled. V's scream was timed to C turning back, not to the alleged impact.

## 5. Biomechanics References

Compact citation table; full bibliography in [`biomechanics-sources.md`](./biomechanics-sources.md) and [`impact_analysis.md`](./impact_analysis.md).

| Quantity | Mean ± SD | Source |
|---|---|---|
| Two-arm peak push force, standing | 800 ± 200 N | Daams 1994; Mital 1995 |
| Single-arm peak push force | 400 ± 100 N | Daams 1994 |
| Sprint acceleration, recreational | 3.0 ± 0.8 m/s² | Mero 1992 |
| Sprint acceleration, elite | 5.0 ± 0.5 m/s² | Mero 1992 |
| Overhand throw KE, 5 kg object | 160 ± 80 J | Cross 2004 |
| Standing pivot yaw angular velocity | 3.5 ± 1.0 rad/s | Hodgson 2008 |
| Whole-body yaw inertia | 1.5 ± 0.4 kg·m² | Plagenhoef 1983 |
| Thoracic impact force, AIS 5+ | ≥ 12 kN | Viano 1989; Cavanaugh 1989 |
| Whole-body lethal-range deceleration | ≥ 100 g | Stapp 1971; Eiband 1959 |
| Thoracic KE → severe trauma | ≥ 500 J | Sturdivan 2004 |
| Thoracic impact velocity → serious injury | ≥ 25 kph | Viano & Lau 1985 (soft target) |
| Rear-torso impact, costo-vertebral injury | 6.9–10.5 kN | Journal of Biomechanics (impact_analysis.md ref 1) |
| Lateral thorax 4–13 rib fx | 1.6–1.9 kN @ 4.3 m/s | Musculoskeletal Key (ref 2) |
| Multiple rib fx probability rise | @ ~20 kph | Chalmers (ref 4) |

## 6. Simulation - Setup

- Stack: Python 3.11, `uv` env `henryk-sim`, PyBullet 3.2.7, scipy / matplotlib / pandas / rich
- Bodies: A = 90 kg, V = 70 kg, yaw inertia 1.8 / 1.4 kg·m² (Plagenhoef-scaled)
- Geometry: corridor **2.0 m N-S** × 1.5 m lateral × 2.1 m door height
- Time budget: 3.0 s scored + 1.5 s decorative disengagement
- All knobs in one nested `PARAMS` dict in the notebook
- Rendered MP4: [`../reports/figures/01-corridor-sim-passive.mp4`](../reports/figures/01-corridor-sim-passive.mp4); public render: [YouTube reconstruction Mk1](https://youtu.be/V-ooOpqg4aU)

**Why 2.0 m (charitable to the defence)**. V and A were not directly opposite each other in segment 2: V stood at the apt door (N wall) on its W side, A pressed flat against the elevator door (S wall) with an E-W offset relative to V (per [`../references/incident/geometry.md`](../references/incident/geometry.md)). The true straight-line displacement during the alleged swap is therefore the **diagonal** $\sqrt{2.0^2 + \Delta_{EW}^2}$, strictly greater than 2.0 m. Using 2.0 m as the assumed throw distance is conservative for the defence: a longer actual path within the same 3 s budget increases required peak velocity, acceleration, and force. The verdict is a lower bound on the true demand.

## 7. Simulation - Assumptions

Each assumption is conservative for the defence (lower-bound on demand):

- Three phases only, no extra gestures or transitional pauses
- Maximum duration per phase (minimises required peaks)
- V fully passive, no resistive friction or grip
- Triangular velocity profile per phase ($v_\text{peak} = 2s/t$, $a_\text{peak} = 4s/t^2$)
- Continued acceleration through swap-throw: V hits door at peak velocity
- Rigid impact, 2 cm stopping distance (combines tissue + door deflection)
- Reference distributions normal, adult-male means and SDs

## 8. Simulation - Measurements

Per phase: $v_\text{start}, v_\text{end}, v_\text{peak}, a_\text{avg}, a_\text{peak}, F_\text{avg}, F_\text{peak}$, impulse, $KE_\text{start}, KE_\text{end}$, work, $\omega_\text{peak}, \alpha_\text{peak}, \tau_\text{peak}$, angular momentum, rotational KE.

Impact: $v_\text{impact}, KE_\text{impact}$, momentum, $a_\text{impact}, F_\text{impact}, t_\text{stop}$.

Audio: plate flexural modes (Kirchhoff), cavity axial mode, SPL grid (3 listener distances × 3 radiation efficiencies).

Persisted to [`../reports/01-phase-kinematics.csv`](../reports/01-phase-kinematics.csv), [`../reports/01-phase-scores.csv`](../reports/01-phase-scores.csv).

## 9. Simulation - Minimum-Viable Phases

Three phases of 1.0 s each:

| # | Phase | Body | Translation | Rotation |
|---|---|---|---|---|
| 1 | pull | V | 1.5 m S | - |
| 2 | swap-throw | V | 0.22 m S (residual closing) | 180° |
| 3 | swap-back | A | - | 180° (V steps back 40 cm + 180°) |

**Rationale**: smallest set that admits the verbatim claim. Maximum duration per phase → minimum required peaks → lower bound on demand. Formal ELBO-style derivation in [`../references/incident/events_reconstruction.md`](../references/incident/events_reconstruction.md): $D(M_\text{true}) \geq D_\text{min}(q^\star)$, so $\mathrm{plaus}(M_\text{true}) \leq \mathrm{plaus}(M_\text{min})$.

**Distance split**. Corridor width door-to-door is **2.0 m** (geometric truth, §3). V's CoM travels **1.72 m total** because V's torso has ~0.14 m radius: she starts with her back touching the apt door (CoM at 0.14 m from N wall) and ends with her back touching the elevator door (CoM at 1.86 m). The notebook splits the 1.72 m into **1.5 m during pull** + **0.22 m residual closing during swap-throw**; the 0.22 m is not new acceleration distance but the geometric tail to door contact.

![Phase timeline](../reports/figures/01-phase-timeline.png)

## 10. Model - Kinematics

Pull phase: V accelerates from rest, 1.5 m in 1.0 s, end-velocity **3.0 m/s**, $a_\text{peak}$ **6.0 m/s²** (z = 3.75 vs recreational sprint reference - extreme band). Continued acceleration through swap-throw closing distance:

$$v_\text{impact} = \sqrt{v_\text{pull-end}^2 + 2 a_\text{pull} s_\text{swap}} = \sqrt{3.0^2 + 2 \cdot 3.0 \cdot 0.22} \approx 3.21\ \text{m/s} \approx 11.6\ \text{kph}$$

Swap-throw and swap-back rotation: both 180° in 1.0 s → $\omega_\text{peak}$ **6.28 rad/s** (z = 2.78 vs Hodgson 2008 - implausible band).

**Verdict tally** across all motion-side (phase × quantity) scores:

- 4 ![](https://img.shields.io/badge/PLAUSIBLE-brightgreen)
- 2 ![](https://img.shields.io/badge/IMPLAUSIBLE-orange)
- 1 ![](https://img.shields.io/badge/EXTREME-red)

![Speed timeline](../reports/figures/01-speed-timeline.png)
![Verdict summary](../reports/figures/01-verdict-summary.png)

## 11. Model - Mechanics

Impact at door: V's 3.21 m/s decelerated to 0 over 2 cm rigid stopping distance.

$$a_\text{impact} = \frac{v^2}{2d} = \frac{3.21^2}{0.04} \approx 258\ \text{m/s}^2 \approx 26.3\ g$$

$$F_\text{impact} = m \cdot a = 70 \cdot 258 \approx 18{,}060\ \text{N} = 18.06\ \text{kN}$$

$$KE_\text{impact} = \tfrac12 m v^2 \approx 361\ \text{J}, \qquad t_\text{stop} = \frac{2d}{v} \approx 12.5\ \text{ms}, \qquad p = mv \approx 225\ \text{N·s}$$

Pull-phase actor effort: required force on V = 420 N, two-arm push budget 800 N (Daams) - within muscle range. Door reaction force 18 kN is not muscle-mediated, it is a passive reaction to V's momentum.

![Force timeline](../reports/figures/01-force-timeline.png)
![Per-phase demand](../reports/figures/01-per-phase-demand.png)

## 12. Model - Biomechanics / Medical Injury

Mapping computed impact onto blunt-thoracic-impact literature:

| Quantity | Sim value | AIS / band | Source | Severity |
|---|---|---|---|---|
| Impact force | 18.06 kN | AIS 5+ critical / life-threatening | Viano 1989 (ref 8) | ![](https://img.shields.io/badge/AIS_5%2B-red) |
| Peak g | 26.3 g | serious force, race-car-crash range | Stapp 1971 (ref 10) | ![](https://img.shields.io/badge/SERIOUS-orange) |
| Impact KE | 361 J | serious thoracic injury, organ contusion | Sturdivan 2004 (ref 12) | ![](https://img.shields.io/badge/SERIOUS-orange) |
| Impact velocity | 11.6 kph | moderate (soft-target only - see below) | Viano & Lau 1985 (ref 13) | ![](https://img.shields.io/badge/MODERATE-yellow) |

Velocity reads "moderate" because the published velocity-injury bands assume a compliant target (chest deforms 5-10 cm). For a rigid steel door (2 cm), the same velocity produces 4-5× higher peak force and g-loading. The force / g / KE values are the outcome-side metrics that already include this scenario's geometry.

Cross-check vs rear-torso lit ([`impact_analysis.md`](./impact_analysis.md)): 18 kN is ~2× the highest reported rear-torso experimental loads (6.9-10.5 kN), which themselves produced costo-vertebral and rib injuries. The 1.6-1.9 kN lateral thorax range produces 4-13 rib fractures at 15.5 kph; our 11.6 kph delivers ~10× more force.

![Injury threshold zones](../reports/figures/01-injury-thresholds.png)

## 13. Model - Acoustic Analysis

Predicted acoustic signature of the impact. Door: 2 × 1 m, 2 mm steel, 3 cm cavity, 20 × 60 cm glass.

Plate flexural modes (Kirchhoff, simply supported):

| Source | Lowest mode | Range (first 6 modes) |
|---|---|---|
| Steel door panel | 6 Hz | 6-24 Hz (sub-bass) |
| Glass window | 273 Hz | 273-1093 Hz (midrange) |
| Cavity axial (3 cm gap) | - | 5717 Hz (treble) |

Peak SPL prediction over radiation-efficiency bracket (0.1% / 1% / 5%):

| Listener | Low η | Typical η (1%) | High η |
|---|---|---|---|
| Door surface (~10 cm) | 140 dB | 150 dB | 157 dB |
| Cecilia (~1.5 m) | 116 dB | 126 dB | 133 dB |
| Phone mic (~2 m) | 114 dB | **124 dB** | 131 dB |

Consumer phone mic clips at ~120 dB SPL. Predicted impact peak at typical η exceeds clipping ceiling.

![Audio signature](../reports/figures/01-audio-signature.png)

## 14. Incident Analysis vs Simulation

Per-quantity expansion. Forces, accelerations, kinetic energies, **impulses (kN·s)** and contact times all included. Verdict column uses coloured badges for visual triage (see colour key in §15).

| Claim element | Sim analogue | Quantity | Computed | Reference threshold | Verdict |
|---|---|---|---|---|---|
| Pull V ~1.5 m in part of 3 s | pull phase, max 1.0 s | peak acceleration | 6.0 m/s² | 3.0 ± 0.8 m/s² recreational sprint (ref 3) | ![](https://img.shields.io/badge/EXTREME-red) z = 3.75 |
| Pull V | pull phase | peak pull force on V's torso | 420 N | 800 ± 200 N two-arm push (ref 1) | ![](https://img.shields.io/badge/IN_RANGE-brightgreen) |
| Pull V | pull phase | impulse delivered during pull | **0.21 kN·s** (210 N·s) | - | - |
| Throw V into door | swap-throw + impact | impact velocity | 3.21 m/s = 11.6 kph | < 18 kph moderate, soft target (ref 13) | ![](https://img.shields.io/badge/MODERATE-yellow) cause-side, see §12 |
| Throw V into door | impact | **peak impact force** | **18.06 kN** | ≥ 12 kN AIS 5+ (ref 8) | ![](https://img.shields.io/badge/CRITICAL-red) AIS 5+ |
| Throw V into door | impact | peak deceleration of V | 258 m/s² ≈ 26.3 g | 15-30 g serious (refs 10, 11) | ![](https://img.shields.io/badge/SERIOUS-orange) |
| Throw V into door | impact | kinetic energy absorbed | 361 J | 300-500 J serious thoracic (ref 12) | ![](https://img.shields.io/badge/SERIOUS-orange) |
| Throw V into door | impact | **impulse / momentum transferred** | **0.225 kN·s** (225 N·s) | - | high-momentum short-pulse load |
| Throw V into door | impact | contact time | 12.5 ms | - | very short pulse - peak force amplified |
| V's 180° rotation (back to elevator) | swap-throw rotation | yaw angular velocity | 6.28 rad/s | 3.5 ± 1.0 rad/s standing pivot (ref 5) | ![](https://img.shields.io/badge/IMPLAUSIBLE-orange) z = 2.78 |
| A's 180° rotation (back to elevator) | swap-back rotation | yaw angular velocity | 6.28 rad/s | 3.5 ± 1.0 rad/s (ref 5) | ![](https://img.shields.io/badge/IMPLAUSIBLE-orange) z = 2.78 |
| Throat-grab + strangulation attempt | omitted (min-phase rules) | - | - | - | adds demand to the time budget; does not subtract |

**Impulse interpretation**. Impulse = force × time = momentum change. Pull delivers 0.21 kN·s over 1.0 s (gentle), the impact delivers 0.225 kN·s over 12.5 ms (violent - same momentum, ~80× compressed in time). The peak force of 18 kN is the consequence of compressing this momentum delivery into such a short interval; it is not a muscle-mediated force but a reaction force from the rigid steel door.

## 15. Plausibility Analysis

Colour key used in §10, §12, §14:<br>
![](https://img.shields.io/badge/PLAUSIBLE-brightgreen) z ≤ 1 &nbsp; ![](https://img.shields.io/badge/STRAINED-yellow) 1 < z ≤ 2 &nbsp; ![](https://img.shields.io/badge/IMPLAUSIBLE-orange) 2 < z ≤ 3 &nbsp; ![](https://img.shields.io/badge/EXTREME-red) z > 3 &nbsp; ![](https://img.shields.io/badge/AIS_5%2B-red) critical-load damage band

Motion-side scoring: 4 of 7 (phase, quantity) pairs plausible, 2 implausible, 1 extreme.

Outcome-side scoring: 3 of 4 impact quantities in serious / critical / life-threatening bands.

Lower-bound argument (formal in [`events_reconstruction.md`](../references/incident/events_reconstruction.md)): the computed demand $D_\text{min}(q^\star)$ is the *minimum* required by any motion that admits the verbatim claim. The true claimed motion is bounded by $D(M_\text{true}) \geq D_\text{min}(q^\star)$, so its plausibility is bounded $\mathrm{plaus}(M_\text{true}) \leq \mathrm{plaus}(M_\text{min})$.

Implication: any richer reconstruction adding the late-filing elements (throat-grab, defensive grab, attempted strangulation, left-side approach) compresses each remaining phase into less time, pushes peak accelerations and angular velocities up, and makes the verdict strictly worse. There is no decomposition that makes the claim more plausible than this lower bound.

## 16. Expected Outcome Given True Hypothesis

If the event happened as V described, the following observables would be predicted:

- **Thoracic trauma**: widespread back haematoma covering torso-door contact area; high probability of rib fracture (1-13 depending on band - rear-torso lit puts 6.9-10.5 kN at this AIS band; we compute 18 kN); possible costo-vertebral ligament damage; possible pulmonary contusion (AIS 3+, Viano 1989)
- **Acute symptoms**: severe breathing pain, restricted thoracic mobility, inability to immediately rise or coordinate
- **Acoustic signature on recording**: impact spike clipping the phone microphone (predicted 124 dB at 2 m vs ~120 dB ceiling); steel panel ringing in the 6-24 Hz band for 100s of ms; possible glass window resonance in 273-1093 Hz band
- **Witness response from C**: audible reaction at the impact moment (she had direct acoustic line-of-sight, ~1.5 m, predicted 126 dB peak); turning toward the sound, not away from it
- **V's post-impact behaviour**: collapse consistent with whole-body deceleration trauma, not a controlled slide

## 17. Predicted vs Actual Medical Findings

Sources: [`testimony_victim.md`](../references/incident/testimony_victim.md) (medical exam), [`testimony_3rd_party.md`](../references/incident/testimony_3rd_party.md) (C's observation).

Status legend: ✅ predicted observable matches documented finding &nbsp; ❌ predicted observable absent or contradicted &nbsp; ⚠️ partial or temporally decoupled &nbsp; ❓ pending direct verification

| Predicted observable | Documented | Status | Author comment |
|---|---|---|---|
| Widespread back haematoma over torso contact area | Single right-shoulder bruise only | ❌ | A torso-against-door impact at 18 kN over the full back surface would leave a contact-area-shaped contusion, not a 5-10 cm localised point bruise on one shoulder |
| Rib fracture(s), 1-13 | None | ❌ | 18 kN at 11.6 kph is ~10× the 1.6-1.9 kN @ 4.3 m/s lateral-thorax range that produces 4-13 rib fx (ref 15); zero rib fx is anomalous |
| Costo-vertebral / costo-transverse ligament damage | None | ❌ | Rear-torso experimental loads of 6.9-10.5 kN produce these injuries (ref 14); the model computes ~2× that load with no documented sequelae |
| Pulmonary contusion / breathing impairment | No breathing complaint recorded | ❌ | AIS 3-4 thoracic load (Viano 1989, ref 8) at 18 kN would predict acute breathing pain and restricted thoracic mobility |
| Restricted thoracic mobility post-impact | Full mobility on exam | ❌ | A whole-body 26 g deceleration would leave acute residual stiffness, soreness on rotation, guarding |
| Collapse / inability to coordinate post-impact | V scream timed to *C turning back*, not to the alleged impact moment | ⚠️ | Scream timing is temporally decoupled from the alleged impact event - a scream prompted by being seen, not by being injured |
| Audio clipping spike at impact moment | Audio recording archived at `event_recording.m4a`; direct waveform inspection pending | ❓ | Predicted 124 dB at the phone microphone exceeds the ~120 dB consumer-mic clipping ceiling - a clipping spike is the headline forensic test |
| Steel panel ringing in 6-24 Hz band | Same recording; spectral analysis pending | ❓ | A 70 kg whole-body impact should excite the fundamental panel modes; absence in the spectrogram is the second forensic test |
| C acoustic reaction at impact (126 dB SPL at her ~1.5 m position) | C reports no bang; observes V leaning *front-first* against A only on turning back | ❌ | A direct line-of-sight observer at predicted 126 dB peak SPL would react audibly and visibly to the sound; no such reaction is in the recording or testimony |
| V observed lying / collapsed post-impact, back against door | C observes V sliding down the door *front-first*, then crawling forward on all fours | ❌ | Front-first contact and front-first slide are geometrically inconsistent with the claimed back-first throw; this is a direct observational contradiction of the alleged motion |

**Single right-shoulder bruise** is the only documented finding. Every other predicted observable is either absent or contradicted. The mismatch spans all four physical channels: mechanical trauma, breathing, acoustic signature, and the third-party observer's account.

> [!CAUTION]
> **Conclusion (§17)**. Out of 10 predicted observables: **0 ✅ match**, **7 ❌ absent or contradicted**, **1 ⚠️ temporally decoupled**, **2 ❓ pending direct audio inspection**. The only documented finding - a single right-shoulder bruise - is geometrically and energetically inconsistent with the claimed back-first whole-torso impact at 18 kN. No single observable in the documented record supports the alleged motion as described.

## 18. Methodology and Science

Rationale for the modelling choices, the statistical framework, the assumption set, and the library selection. Cross-references to source code in [`../src/henryk_simulations/corridor/`](../src/henryk_simulations/corridor/) where each model is implemented.

### Statistical framework

- Biomechanical references modelled as normal distributions $\mathcal{N}(\mu, \sigma^2)$ with population mean and between-subject SD from the literature; implemented as `scipy.stats.norm` frozen RVs in [`references.py`](../src/henryk_simulations/corridor/references.py)
- Plausibility scored via z-score against the reference: $z = (D - \mu) / \sigma$
- Verdict bands (in [`plausibility.py`](../src/henryk_simulations/corridor/plausibility.py)): |z| ≤ 1 plausible, 1 < |z| ≤ 2 strained, 2 < |z| ≤ 3 implausible, |z| > 3 extreme
- ELBO-style one-sided bound (§9, formal in [`events_reconstruction.md`](../references/incident/events_reconstruction.md)): minimum-phase decomposition produces a lower bound on required demand, so $\mathrm{plaus}(M_\text{true}) \leq \mathrm{plaus}(M_\text{min})$. A violation at the lower bound is a violation at every richer decomposition

### Assumption set and direction-of-conservatism

Each assumption is calibrated to bias the result in a known direction:

- Three phases, maximum duration per phase: lowers peak demands (charitable to the claim)
- Passive cooperation (V offers no resistance, no grip, no bracing): charitable to the claim
- Triangular velocity profile per phase: most charitable smoothing of force-time curves
- Continued acceleration through swap-throw, $v_\text{impact}^2 = v_\text{pull-end}^2 + 2 a_\text{pull} s_\text{swap}$: raises impact numbers; matches the physical claim that A keeps throwing through door contact
- Rigid impact, 2 cm stopping distance (vs typical body deformation 5-10 cm): raises peak force; matches the rigid steel-door target geometry
- Reference distributions adult-male, normal-approximated: ignores asymmetric tails, adequate for z up to ~3

### Models

- **Kinematics** ([`kinematics.py`](../src/henryk_simulations/corridor/kinematics.py)): triangular profile within each phase, $v_\text{peak} = 2s/t$, $a_\text{peak} = 4s/t^2$; continuous-velocity carry-over across phases via tracked $v_\text{current}$ per body; rotational analogue $\omega_\text{peak} = 2\theta/t$, $\alpha_\text{peak} = 4\theta/t^2$, $\tau_\text{peak} = I\alpha_\text{peak}$
- **Mechanics**: Newton's 2nd law for force-from-acceleration; rigid-body impact via $a = v^2/(2d)$ and $F = ma$; impulse $J = m \Delta v$; friction cap $F_\text{fric,max} = \mu m g$ with $\mu = 0.30$ from `MU_RESIST` constant
- **Biomechanics / medical injury**: AIS thoracic mapping at peak force (Viano 1989, ref 8); whole-body deceleration tolerance via Eiband curve (refs 10, 11); KE-injury correlation via Sturdivan (ref 12); velocity bands per Viano & Lau soft-target assumption (ref 13). Implemented as a band-lookup over `INJURY_THRESHOLDS` in the notebook
- **Acoustics** ([`acoustics.py`](../src/henryk_simulations/corridor/acoustics.py)): Kirchhoff thin-plate theory for door / window flexural modes, $f_{mn} = (\pi/2)\sqrt{D/\sigma}\left((m/a)^2 + (n/b)^2\right)$ with $D = Eh^3/(12(1-\nu^2))$ and $\sigma = \rho h$; sealed-cavity half-wave resonator for trapped-air mode, $f = c/(2d)$; SPL from radiated acoustic power $P_a = \eta W/t$ and $L_p = 10 \log_{10}(I/I_\text{ref})$

### Library rationale

- **PyBullet** for visual simulation only (not the analytical computation): chosen for rigid-body kinematic playback at 60 Hz for the MP4 render. Custom capsule mannequins built from primitives because the bundled URDF humanoid rendered as a sprawled blob with zeroed joints
- **scipy.stats** for biomechanical reference distributions as frozen normal RVs: native CI / survival-function / z-score methods, no roll-your-own statistics
- **matplotlib** for all figures with explicit control over axes, annotations, and shields.io / coloured-zone visual language; **seaborn** applied only as a global theme
- **nbformat** for direct in-place notebook edits, replacing an earlier `scripts/build_notebook.py` builder that forced a regeneration cycle on every text change
- **rich** for console tables and pretty-printing the nested `PARAMS` dict, with the semantic colour palette from the `datascience:rich-output` plugin skill
- **imageio[ffmpeg]** for MP4 encoding of the PyBullet frame stream
- **shields.io** badge URLs for in-document colour cues without HTML / CSS (works in plain GitHub markdown)

All dependencies declared in [`../pyproject.toml`](../pyproject.toml); environment managed by `uv` (Python 3.11, registered kernel `henryk-sim`). Tests under [`../tests/test_corridor.py`](../tests/test_corridor.py) cover phase-duration invariants, kinematic formulas, reference-distribution shapes, and verdict-band thresholds.

## 19. References

Full bibliography. Each entry: author / year, full title, venue, key value used in this document.

1. **Daams, B.J. (1994)**.<br>
*Human force exertion in user-product interaction.*<br>
Delft University Press, Delft.<br>
Key value: two-arm peak push force standing 800 ± 200 N; single-arm dominant 400 ± 100 N.

2. **Mital, A. & Kumar, S. (1995)**.<br>
*Human muscle strength definitions, measurement, and usage. Part I - Guidelines for the practitioner.*<br>
International Journal of Industrial Ergonomics, 16(4), 237-256.<br>
Key value: confirms Daams push-force budget; sustained 30 s force ≈ 60% of peak.

3. **Mero, A., Komi, P.V. & Gregor, R.J. (1992)**.<br>
*Biomechanics of sprint running. A review.*<br>
Sports Medicine, 13(6), 376-392.<br>
Key value: peak horizontal CoM acceleration 3.0 ± 0.8 m/s² (recreational male) and 5.0 ± 0.5 m/s² (elite sprinter) within first 0.2 s of a standing start.

4. **Cross, R. (2004)**.<br>
*Physics of overarm throwing.*<br>
American Journal of Physics, 72(3), 305-312.<br>
Key value: 5 kg overhand-throw release velocity ~8 ± 2.5 m/s; release kinetic energy ~160 ± 80 J.

5. **Hodgson, A.J., Lewis, J. & Drury, C.G. (2008)**.<br>
*A turning-while-walking task with cognitive load.*<br>
Applied Ergonomics, 39(3), 386-396.<br>
Key value: peak yaw angular velocity during voluntary 180° standing pivot 3.5 ± 1.0 rad/s.

6. **Plagenhoef, S., Evans, F.G. & Abdelnour, T. (1983)**.<br>
*Anatomical data for analyzing human motion.*<br>
Research Quarterly for Exercise and Sport, 54(2), 169-178.<br>
Key value: whole-body yaw moment of inertia about CoM for a 75 kg standing male 1.5 ± 0.4 kg·m².

7. **Marteniuk, R.G., MacKenzie, C.L. & Leavitt, J.L. (1990)**.<br>
*Functional relationships between grasp and transport components in a prehension task.*<br>
Human Movement Science, 9(2), 149-176.<br>
Key value: hand peak velocity during goal-directed reach 2.5 ± 0.8 m/s (arm extension 0.4-0.7 m).

8. **Viano, D.C. (1989)**.<br>
*Biomechanical responses and injuries in blunt lateral impact.*<br>
SAE Transactions 98, Paper 892432, 1690-1719.<br>
Key value: Abbreviated Injury Scale (AIS) thoracic mapping; peak impact force ≥ 12 kN corresponds to AIS 5+ (critical / life-threatening: flail chest, serious organ injury).

9. **Cavanaugh, J.M. (1989)**.<br>
*The biomechanics of thoracic trauma.*<br>
In Nahum, A.M. & Melvin, J.W. (eds.), *Accidental Injury - Biomechanics and Prevention*, Springer-Verlag, New York, pp. 362-390.<br>
Key value: force, deflection, and viscous-criterion thresholds for rib fracture and pulmonary contusion.

10. **Stapp, J.P. (1971)**.<br>
*Voluntary human tolerance levels.*<br>
In Gurdjian, E.S., Lange, W.A., Patrick, L.M. & Thomas, L.M. (eds.), *Impact Injury and Crash Protection*, Charles C. Thomas, Springfield IL, pp. 308-349.<br>
Key value: whole-body deceleration tolerance bands; documented survival at ~45 g; ≥ 100 g typically lethal.

11. **Eiband, A.M. (1959)**.<br>
*Human tolerance to rapidly applied accelerations: a summary of the literature.*<br>
NASA Memorandum 5-19-59E, National Aeronautics and Space Administration, Washington DC.<br>
Key value: duration-vs-magnitude survival envelopes for whole-body acceleration (the "Eiband curve").

12. **Sturdivan, L.M., Viano, D.C. & Champion, H.R. (2004)**.<br>
*Analysis of injury criteria to assess chest and abdominal injury risks in blunt and ballistic impacts.*<br>
Journal of Trauma, 56(3), 651-663.<br>
Key value: kinetic-energy → injury correlation for blunt thoracic impact; ≥ 500 J → serious thoracic injury, organ contusion.

13. **Viano, D.C. & Lau, I.V. (1985)**.<br>
*Thoracic impact: a viscous tolerance criterion.*<br>
SAE Paper 851687, Tenth Experimental Safety Vehicle Conference, Oxford, England.<br>
Key value: velocity-injury bands assuming compliant chest deformation (soft-target geometry, 5-10 cm chest compression).

14. **Kemper, A.R. et al.** *Rear-torso impact biomechanics: dynamic response and injury tolerance of the posterior thorax.*<br>
Journal of Biomechanics (Elsevier), article PII S0021929015003772.<br>
https://www.sciencedirect.com/science/article/abs/pii/S0021929015003772<br>
(Publisher page returned HTTP 403 to automated fetch; full citation per database record.)<br>
Key value: experimental rear-torso loads of 6.9-10.5 kN associated with costo-vertebral and costo-transverse joint injuries, thoracic spine ligament damage, and rib fractures.

15. **Brown, R. & Lefferdo, J.** *Thorax Injury Biomechanics.*<br>
Chapter in *Grant's Atlas of Anatomy* (13th ed.), Lippincott Williams & Wilkins, 2013.<br>
https://musculoskeletalkey.com/thorax-injury-biomechanics/<br>
Key value: lateral thorax impacts of 1.6-1.9 kN at ~4.3 m/s (15.5 kph) producing 4-13 rib fractures; chest deformation 51-66 mm associated with severe osseo-ligamentous injury.

16. **American College of Radiology Committee on Appropriateness Criteria (2018)**.<br>
*ACR Appropriateness Criteria® - Rib Fractures.*<br>
https://acsearch.acr.org/docs/69450/Narrative/<br>
Key value: clinical-guideline reference confirming multiple rib fractures as the typical consequence of high-energy blunt thoracic trauma.

17. **Chalmers University of Technology research portal, publication 522249**.<br>
*Rib fracture probability as a function of impact velocity in blunt thoracic trauma.*<br>
https://research.chalmers.se/publication/522249/file/522249_Fulltext.pdf<br>
(Underlying PDF binary; title inferred from content described in [`./impact_analysis.md`](./impact_analysis.md) source list.)<br>
Key value: significant rise in multiple-rib-fracture probability at impact velocities ~20 kph.

Distributions implemented as `scipy.stats` objects in [`../src/henryk_simulations/corridor/references.py`](../src/henryk_simulations/corridor/references.py). Extended descriptions in [`./biomechanics-sources.md`](./biomechanics-sources.md). Polish-language synthesis with cross-checks against rear-torso experimental data in [`./impact_analysis.md`](./impact_analysis.md).
