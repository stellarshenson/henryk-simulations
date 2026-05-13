# Events Reconstruction

Minimum-viable stage reconstruction of the contested 3-second corridor incident. Geometry is fixed in `geometry.md`; testimony content is in `testimony_victim.md`, `testimony_3rd_party.md` and `testimony_victoria_inconsistencies.md` (all sibling files in this folder).

## Methodology

This is a **minimum-phases reconstruction**: the smallest set of stages that maps the verbatim claim onto separable physical motions. **No additional phases, sub-movements, gestures, hand re-positionings, body adjustments, or transitional pauses are added.** Each stage is given the maximum duration the 3 s budget allows for that action, which minimises the required peak velocities, accelerations and forces.

The point of using the minimum-phase decomposition is to **stress test the most plausible minimal action setup that fits the 3 s time window**. If even this maximally-charitable reconstruction produces extreme demands (z > 3 against population biomechanical references), the contested claim is mechanically inconsistent regardless of how it is decomposed. Any more elaborate reconstruction (with the throat-grab attempt, the defensive hand-grab, the strangulation attempt, the left-side approach, or any other element from Victoria's later filings) would compress each remaining phase into less time and push the demands higher.

The verdict is therefore a **lower bound** on what the alleged motion would require.

### Theoretical formulation

Let:

- $\Omega$ = the space of all motion sequences consistent with the geometry, the 3 s budget, and the verbatim claim
- $M \in \Omega$ = the true (unobserved) motion
- $D : \Omega \to \mathbb{R}^+$ = a kinematic demand functional (peak force, peak acceleration, kinetic energy, peak angular velocity, etc.)
- $R$ = the population biomechanical reference distribution for that quantity
- $\mathrm{plaus}(M) = \Pr_{X \sim R}[\,X \geq D(M)\,]$ = the fraction of the reference population able to meet the demand

For a parametrised family of phase decompositions $\{q\}$, let $\Omega_q \subseteq \Omega$ be the motions admitted by decomposition $q$, and

$$D_{\min}(q) \;=\; \inf_{M' \in \Omega_q} D(M')$$

the minimum demand any motion in that family imposes. The **minimum-phases reconstruction** $q^\star$ uses the smallest phase set consistent with the claim:

$$q^\star \;=\; \arg\min_q |q| \quad \text{s.t. } q \text{ admits the verbatim claim.}$$

By construction $M_{\text{true}} \in \Omega_{q^\star}$, so

$$D(M_{\text{true}}) \;\geq\; D_{\min}(q^\star)$$

and because $X \mapsto \Pr[X \geq \cdot]$ is monotonically non-increasing in its argument,

$$\mathrm{plaus}(M_{\text{true}}) \;=\; \Pr_{X \sim R}[\,X \geq D(M_{\text{true}})\,] \;\leq\; \Pr_{X \sim R}[\,X \geq D_{\min}(q^\star)\,] \;=\; \mathrm{plaus}(M_{\min}).$$

So $\mathrm{plaus}(M_{\min})$ is an **upper bound** on the true plausibility (equivalently, $D_{\min}(q^\star)$ is a lower bound on the true required demand). If $\mathrm{plaus}(M_{\min})$ is small (the $z$-score on $D_{\min}$ is large against $R$), $\mathrm{plaus}(M_{\text{true}})$ is at least as small.

### ELBO analogy

In variational inference the evidence lower bound is

$$\log p(x) \;=\; \log \int p(x, z)\,dz \;\geq\; \mathbb{E}_{q(z\mid x)}\!\left[\,\log \frac{p(x, z)}{q(z\mid x)}\,\right] \;=\; \mathcal{L}(q),$$

with $\log p(x) - \mathcal{L}(q) = \mathrm{KL}\!\left(q(z\mid x) \,\|\, p(z\mid x)\right) \geq 0$. Maximising $\mathcal{L}(q)$ over a variational family $\{q\}$ approaches the true $\log p(x)$ **from below**.

Structurally:

|  | Variational inference (ELBO) | Min-phases reconstruction |
|---|---|---|
| Intractable target | $\log p(x)$ | $\mathrm{plaus}(M_{\text{true}})$ |
| Tractable surrogate | $\mathcal{L}(q)$ | $\mathrm{plaus}(M_{\min})$ |
| Bound direction | lower bound on the target | upper bound on the target |
| Optimisation move | maximise $\mathcal{L}(q)$ over $q$ | minimise $D_{\min}(q)$ over $q$ (most charitable decomposition) |
| Guarantee | improving the bound never hurts the true objective | a violation of the bound implies a violation of the true |

If $D_{\min}(q^\star) \gg R$ (the lower-bound demand greatly exceeds population reference), then $D(M_{\text{true}}) \gg R$ too - regardless of how the actual motion is decomposed.

## Inputs

- **Geometry**: see `geometry.md` for corridor topology, actor positions, props ([Box] briefcase, [Str] stroller, D apartment-door swing).
- **Audio recording**: full audio of the visit and the contested moment, tracked in the repo at [`../../data/external/event_audio/event_recording.m4a`](../../data/external/event_audio/event_recording.m4a). This is the source for `testimony_3rd_party.md` and for Victoria's verbatim live exclamations in `testimony_victim.md`.
- **Testimonies**: victim, third-party (court social curator), and Victoria's inconsistency log.

## Stages

| # | Stage | Duration | What happens |
|---|---|---|---|
| 0 | **Setup** | pre-timer | Both at apartment door. Andrew calls to the child. Victoria takes a toy. Victoria asks Cecilia to step aside and Andrew to step aside; Andrew presses flat against the elevator door (max-retreat). |
| 1 | **Approach** | pre-timer | Victoria **places the toy on the floor in the corridor** to entice the child outside. Cecilia takes three steps and turns away briefly to clear the line for the rolled toy. |
| 2 | **Pull** | ~1.0 s | (claimed by V) Andrew pulls Victoria across the corridor. Victoria's CoM translates ~1.5 m southward from the apartment door area into segment 2. |
| 3 | **Swap and throw** | ~1.0 s | (claimed by V) Positions exchange; Victoria's back impacts the elevator door; Victoria rotates 180° tracking Andrew. **Impact** event - the kinematic singularity. |
| 4 | **Swap again** | ~1.0 s | (claimed by V) Andrew rotates 180° (back to elevator); Victoria steps back 40 cm + rotates 180°. End state has Victoria standing in front of Andrew (the state Cecilia observed; the police arrived after the event and only took testimonies). |
| 5 | **Disengage** | post-timer | Victoria slides down the door surface, crawls on all fours, screams (timed to Cecilia turning back). Not part of any scored kinematic phase. |

Stages 2-4 are the contested 3.0 s window. Stages 0, 1, 5 are observed setup and post-event aftermath.

## Per-stage kinematics

Computed in `../../notebooks/01-kj-corridor-kinematics.ipynb`, with full numbers in `../../reports/01-phase-kinematics.csv` and `../../reports/01-phase-scores.csv`. The headline (no-resistance / worst-case) verdicts:

| Stage | v_end | a_peak | F_peak | KE | ω_peak | Headline verdict |
|---|---|---|---|---|---|---|
| Pull | 3.0 m/s | 6.0 m/s² | 420 N | 315 J | - | a_peak extreme (z=3.75) |
| Swap+throw | 0 (impact) | 2.0 m/s² | 140 N | 35 J | 6.28 rad/s | ω implausible (z=2.78); impact F = 15.75 kN (22.9 g) over 2 cm stopping distance |
| Swap-back | 0 | 2.0 m/s² | 112 N | 22 J | 6.28 rad/s | ω implausible (z=2.78) |

Configurable knobs in the notebook config cell: `PHASE_DURATIONS` (per-stage time budget), `STOPPING_DISTANCE_CM` (impact stopping distance).

## Geometric constraints (from `geometry.md`)

- Andrew is **pressed flat against the elevator door** at his max-retreat position - cannot move further south.
- Elevator door is on Victoria's **front-right diagonal** (SW of her standing position on the W side of the apartment door envelope).
- Briefcase [Box] occupies the floor space east of Andrew, blocking the eastward lateral step-out.
- The 2 m N-S corridor width is the throw distance from V's apt-door position to the elevator door across segment 2.

## Disengagement (rendering-only)

Rendered in the simulation MP4 as a 1.5 s tail after the 3 s scored window - V crouches forward and slides back through the apartment doorway. Not part of any kinematic phase; included for visual continuity with Victoria's "and then she fell" narrative.

## What this analysis does not establish

- Whether the alleged motion actually occurred (only kinematic plausibility under the most charitable cooperation model).
- Whether the actual injury pattern (single right-shoulder bruise vs widespread thoracic trauma) is consistent with the computed impact force - see `../../docs/impact_analysis.md`.
- The contradictions between Victoria's evolving narrative and the third-party observation - see `testimony_victoria_inconsistencies.md` and `testimony_3rd_party.md`.
