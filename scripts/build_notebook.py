"""Build notebooks/01-kj-corridor-kinematics.ipynb programmatically via nbformat.

Run:
    .venv/bin/python scripts/build_notebook.py

This is a build helper, not part of the corridor module. It generates the
notebook from a single source-of-truth so we do not hand-edit JSON.
"""

from __future__ import annotations

from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

OUT = Path(__file__).parents[1] / "notebooks" / "01-kj-corridor-kinematics.ipynb"

HEADER_MD = """\
# Corridor Two-Body Kinematic Plausibility Simulation

Author: Andrew Jelen<br>
Approach: 3-phase analytical decomposition of the contested two-body movement sequence in a 2 m corridor over 3 s, comparing the per-phase kinematic demands against published biomechanical reference distributions with 95% confidence intervals.

## Events reconstruction (3 phases over 3 s)

Corridor topology (V = Victoria, A = Andrew; `|` = wall/door, `..` = corridor space):

```
pre-timer    |V A .. |       A has approached V; both stand near the apartment door
t = 0.0 s    |V A .. |       timer starts
t = 1.0 s    | .. VA |       after pull
t = 2.0 s    | .. AV*|       after swap+throw; V's back impacts elevator door (*)
t = 3.0 s    | .. VA |       after swap-back; A ends at elevator with back to it
```

Initial positions: V at x=0.1 m (apartment doorway), A at x=0.5 m (just inside the corridor, in front of V). Both face the elevator at +x. V's facing direction tracks A continuously, rotating 180 degrees each time positions swap.

| # | Phase | Duration | V motion | A motion | Notes |
|---|---|---|---|---|---|
| 1 | Pull | 1.0 s | translates 1.5 m | retreats backward 1.3 m | A drags V toward elevator |
| 2 | Swap+throw | 1.0 s | translates 0.5 m + rotates 180 deg | swaps to V's other side | V's back impacts elevator door |
| 3 | Swap-back | 1.0 s | translates 0.5 m + rotates 180 deg | rotates 180 deg + translates 0.5 m | A ends at elevator with back to it |

Per-phase kinematic budgets derived directly from each phase's duration via the triangular velocity profile:

- v_peak = 2 * displacement / duration
- a_peak = 4 * displacement / duration^2
- F_peak = mass * a_peak
- impulse = mass * v_peak
- kinetic energy = 0.5 * mass * v_peak^2
- omega_peak = 2 * rotation_angle / duration

The analysis answers: what peak velocities, accelerations, forces, impulses, kinetic energies and angular velocities are *required* for each phase, and how do those values compare to what adult males in the relevant reference populations can actually produce?

## Scoring rubric

| z-score above reference mean | Verdict |
|---|---|
| z <= 1 | plausible |
| 1 < z <= 2 | strained |
| 2 < z <= 3 | implausible |
| z > 3 | extreme |

Two cooperation models are computed: **passive** (deadweight, no resistance) and **small resistance** (friction-equivalent counter-force plus active brake). Full reconstruction narrative in `docs/events_reconstruction.md`; impact-force analysis at the elevator door in `docs/impact_analysis.md`.
"""

IMPORTS_CODE = """\
# Imports
from __future__ import annotations

import math  # standard library
from pathlib import Path

# Numerical / data
import numpy as np
import pandas as pd

# Plotting
import matplotlib.pyplot as plt
import seaborn as sns

# Rich console for tabular output
from rich.console import Console
from rich.table import Table

# Project modules
from henryk_simulations.corridor import (
    PhaseResult,
    PlausibilityScore,
    Verdict,
    compute_scenario,
    default_library,
    default_scenario,
    score_phase,
)
from henryk_simulations.corridor.kinematics import (
    G,
    actor_effort_for_translation,
    compute_phase_kinematics,
)
from henryk_simulations.corridor.plausibility import (
    score_reach_phase,
    score_rotation_phase,
    score_translation_phase,
)
from henryk_simulations.corridor.plots import (
    plot_acceleration_over_time,
    plot_corridor_overhead,
    plot_force_over_time,
    plot_impulse_over_time,
    plot_per_phase_demand,
    plot_phase_timeline,
    plot_reference_overlay,
    plot_speed_over_time,
    plot_verdict_summary,
)

console = Console()
sns.set_theme(style="whitegrid", context="notebook")
FIG_DIR = Path("../reports/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)
"""

SEED_CODE = """\
# Reproducibility - bootstrap CIs sample from references
SEED = 42
np.random.seed(SEED)
rng = np.random.default_rng(SEED)
"""

CONFIG_CODE = """\
# Scenario configuration - per-phase time budget is editable here.
# Total time is the sum of phase durations; each phase's kinematic demand
# scales as v_peak = 2*s/t, a_peak = 4*s/t^2 so shorter phases mean higher
# required peaks.
PHASE_DURATIONS = {
    "pull":       1.0,  # s - A retreats backward pulling V toward elevator
    "swap-throw": 1.0,  # s - positions swap, V impacts elevator, V rotates 180 deg
    "swap-back":  1.0,  # s - positions swap back, A rotates 180 deg, V rotates 180 deg
}
sc = default_scenario(phase_durations=PHASE_DURATIONS)
lib = default_library()

cfg_table = Table(title="Scenario configuration", show_header=True, header_style="bold")
cfg_table.add_column("Parameter")
cfg_table.add_column("Value")
cfg_table.add_row("corridor width (door-to-door)", f"{sc.geometry.corridor_width:.2f} m")
cfg_table.add_row("corridor lateral", f"{sc.geometry.corridor_lateral:.2f} m")
cfg_table.add_row("Andrew mass", f"{sc.bodies.h_mass:.0f} kg")
cfg_table.add_row("Victoria mass", f"{sc.bodies.m_mass:.0f} kg")
cfg_table.add_row("Andrew yaw inertia", f"{sc.bodies.yaw_inertia_h:.2f} kg m^2")
cfg_table.add_row("Victoria yaw inertia", f"{sc.bodies.yaw_inertia_m:.2f} kg m^2")
cfg_table.add_row("total time", f"{sc.total_time:.2f} s")
cfg_table.add_row("phase count", f"{len(sc.phases)}")
console.print(cfg_table)
"""

GEOMETRY_FIG_CODE = """\
# Corridor overhead schematic
fig_corr = plot_corridor_overhead(
    sc.geometry,
    sc.bodies,
    out_path=FIG_DIR / "01-corridor-geometry.png",
)
plt.show()
"""

PHASES_CODE = """\
# Phase decomposition table
ph_table = Table(title="3-phase decomposition", show_header=True, header_style="bold")
for col in ("#", "phase", "kind", "body", "duration (s)", "translation (m)", "rotation (deg)", "notes"):
    ph_table.add_column(col)
notes_map = {
    "pull": "A retreats backward toward elevator pulling V along (1.5 m of V's 2 m total)",
    "swap-throw": "Positions exchange + V's back impacts elevator door + V rotates 180 deg tracking A",
    "swap-back": "Positions exchange back; A rotates 180 deg to face away (back to elevator); V rotates 180 deg",
}
for idx, phase in enumerate(sc.phases):
    deg = phase.rotation * 180 / math.pi if phase.rotation else 0
    ph_table.add_row(
        str(idx + 1),
        phase.name,
        phase.kind,
        phase.body,
        f"{phase.duration:.2f}",
        f"{phase.translation:.2f}" if phase.translation else "-",
        f"{deg:.0f}" if deg else "-",
        notes_map.get(phase.name, ""),
    )
console.print(ph_table)
"""

PHASE_SUMMARY_CODE = """\
# Per-phase summary table: peak values + verdict bands per (phase, quantity)
summary_table = Table(title="Per-phase peak demands and verdicts", show_header=True, header_style="bold")
for col in ("phase", "quantity", "required", "ref mean +/- sd", "x mean", "z", "verdict"):
    summary_table.add_column(col)

verdict_style = {
    "plausible": "green",
    "strained": "yellow",
    "implausible": "red",
    "extreme": "bold red",
}
for s in scores:
    summary_table.add_row(
        s.phase_name,
        s.quantity_label,
        f"{s.required_value:,.2f} {s.units}",
        f"{s.reference_mean:.2f} +/- {s.reference_sd:.2f} {s.units}",
        f"{s.multiple_of_mean:.2f} x",
        f"{s.z:+.2f}",
        f"[{verdict_style.get(s.verdict.value, 'white')}]{s.verdict.value}[/]",
    )
console.print(summary_table)
"""

TIMELINE_CODE = """\
# Phase timeline gantt
fig_timeline = plot_phase_timeline(
    sc.phases,
    sc.phase_starts,
    total_time=sc.total_time,
    out_path=FIG_DIR / "01-phase-timeline.png",
)
plt.show()
"""

KINEMATICS_CODE = """\
# Per-phase kinematics, passive vs small-resistance
rows = []
for resistance in ("passive", "small"):
    results = compute_scenario(sc, resistance=resistance)
    for r in results:
        rows.append({
            "resistance": resistance,
            "phase": r.phase_name,
            "kind": r.kind,
            "body": r.body,
            "mass_kg": r.mass,
            "duration_s": r.duration,
            "distance_m": r.distance,
            "v_peak_m_s": round(r.v_peak, 3),
            "a_peak_m_s2": round(r.a_peak, 3),
            "a_peak_g": round(r.a_peak_g, 3),
            "f_peak_N": round(r.f_peak, 1),
            "f_resist_N": round(r.f_resist, 1),
            "impulse_N_s": round(r.impulse, 1),
            "ke_J": round(r.kinetic_energy, 1),
            "omega_peak_rad_s": round(r.omega_peak, 3),
            "alpha_peak_rad_s2": round(r.alpha_peak, 3),
            "torque_peak_Nm": round(r.torque_peak, 1),
            "rot_ke_J": round(r.rotational_ke, 1),
            "reach_v_peak_m_s": round(r.reach_v_peak, 3),
            "reach_f_peak_N": round(r.reach_f_peak, 1),
        })
results_df = pd.DataFrame(rows)
results_df.head(20)
"""

THROW_SANITY_CODE = """\
# Headline numbers for each phase based on its time budget
all_results = compute_scenario(sc, resistance="passive")
hdr_table = Table(title="Phase headline kinematics (passive, per time budget)", show_header=True, header_style="bold")
for col in ("phase", "duration (s)", "v_peak (m/s)", "a_peak (m/s^2, g)", "F_peak (N)", "KE (J)", "impulse (N s)", "omega_peak (rad/s)"):
    hdr_table.add_column(col)
for r in all_results:
    hdr_table.add_row(
        r.phase_name,
        f"{r.duration:.2f}",
        f"{r.v_peak:.2f}" if r.v_peak else "-",
        f"{r.a_peak:.2f} ({r.a_peak_g:.2f}g)" if r.a_peak else "-",
        f"{r.f_peak:.0f}" if r.f_peak else "-",
        f"{r.kinetic_energy:.0f}" if r.kinetic_energy else "-",
        f"{r.impulse:.0f}" if r.impulse else "-",
        f"{r.omega_peak:.2f}" if r.omega_peak else "-",
    )
console.print(hdr_table)
"""

ACTOR_EFFORT_CODE = """\
# Actor effort and friction cap during the pull phase
throw = next(r for r in compute_scenario(sc, resistance="passive") if r.phase_name == "pull")
eff = actor_effort_for_translation(throw, actor_mass=sc.bodies.h_mass)
console.print("[bold]Actor effort budget[/bold]")
console.print(f"  required force on M : {eff['f_required_N']:.0f} N")
console.print(f"  friction cap (H mass {sc.bodies.h_mass:.0f} kg, mu 0.30): {eff['f_friction_cap_N']:.0f} N")
console.print(f"  feasible            : {eff['feasible']}")
console.print(f"  headroom ratio      : {eff['headroom_ratio']:.2f}")
"""

REFERENCES_CODE = """\
# Reference distributions
ref_rows = []
for key, ref in lib.refs.items():
    lo, hi = ref.ci(0.95)
    ref_rows.append({
        "key": key,
        "name": ref.name,
        "units": ref.units,
        "mean": round(ref.mean, 3),
        "sd": round(ref.sd, 3),
        "ci95_lo": round(lo, 3),
        "ci95_hi": round(hi, 3),
        "population": ref.population,
        "citation": ref.citation,
    })
ref_df = pd.DataFrame(ref_rows)
ref_df
"""

SCORING_CODE = """\
# Score each phase against the most appropriate reference for each kinematic demand
results_passive = compute_scenario(sc, resistance="passive")

# Map phase -> chosen references. A translate phase that also has a rotation
# (Victoria's 360 deg yaw during the throw) is scored for both quantities.
def score_all(results):
    scores: list[PlausibilityScore] = []
    for r in results:
        if r.kind == "translate" and r.f_peak > 0:
            scores += score_translation_phase(
                r,
                accel_ref=lib["sprint_acceleration_recreational"],
                force_ref=lib["push_force_two_arm"],
                energy_ref=lib["throw_kinetic_energy"] if r.phase_name in ("pull", "swap-throw") else None,
            )
        if r.omega_peak > 0:
            scores += score_rotation_phase(r, omega_ref=lib["yaw_angular_velocity_pivot"])
        if r.kind == "reach" and r.reach_v_peak > 0:
            scores += score_reach_phase(r, arm_ref=lib["arm_swing_velocity"])
    return scores

scores = score_all(results_passive)
score_df = pd.DataFrame([
    {
        "phase": s.phase_name,
        "quantity": s.quantity_label,
        "required": round(s.required_value, 3),
        "units": s.units,
        "ref": s.reference_name,
        "ref_mean": round(s.reference_mean, 3),
        "ref_sd": round(s.reference_sd, 3),
        "z": round(s.z, 2),
        "x_mean": round(s.multiple_of_mean, 2),
        "verdict": s.verdict.value,
    }
    for s in scores
])
score_df
"""

VERDICT_SUMMARY_CODE = """\
# Lollipop summary of z-scores
fig_verdict = plot_verdict_summary(scores, out_path=FIG_DIR / "01-verdict-summary.png")
plt.show()
"""

DEMAND_PLOT_CODE = """\
# Per-phase demand: acceleration, force, KE (passive vs small)
fig_demand = plot_per_phase_demand(
    results_df[results_df["a_peak_m_s2"] > 0],
    columns=["a_peak_m_s2", "f_peak_N", "ke_J"],
    out_path=FIG_DIR / "01-per-phase-demand.png",
    title="Per-phase translation demand (passive vs small-resistance)",
)
plt.show()
"""

TIMELINES_CODE = """\
# Four time-series plots: speed, acceleration, force, cumulative impulse
fig_v = plot_speed_over_time(
    sc, results_passive, out_path=FIG_DIR / "01-speed-timeline.png"
)
plt.show()

fig_accel = plot_acceleration_over_time(
    sc, results_passive, out_path=FIG_DIR / "01-acceleration-timeline.png"
)
plt.show()

fig_F = plot_force_over_time(
    sc, results_passive, out_path=FIG_DIR / "01-force-timeline.png"
)
plt.show()

fig_p = plot_impulse_over_time(
    sc, results_passive, out_path=FIG_DIR / "01-impulse-timeline.png"
)
plt.show()
"""

REFERENCE_OVERLAY_CODE = """\
# Required values overlaid on reference distributions
# Pick the union of references that received at least one score
ref_used = []
for s in scores:
    if not any(r.name == s.reference_name for r in ref_used):
        ref_used.append(next(r for r in lib.refs.values() if r.name == s.reference_name))
fig_overlay = plot_reference_overlay(
    scores,
    ref_used,
    out_path=FIG_DIR / "01-reference-overlay.png",
)
plt.show()
"""

ENERGY_BREAKDOWN_CODE = """\
# Energy budget for the pull phase (largest translational demand)
throw_r = next(r for r in results_passive if r.phase_name == "pull")
push_budget_two_arm = lib["push_force_two_arm"].mean
throw_ke_ref = lib["throw_kinetic_energy"]

console.print(f"[bold]Throw energy budget[/bold]")
console.print(f"  kinetic energy delivered to M : {throw_r.kinetic_energy:,.0f} J")
console.print(f"  reference for 5 kg overhand throw: {throw_ke_ref.mean:.0f} +/- {throw_ke_ref.sd:.0f} J")
console.print(f"  multiple of reference mean     : {throw_r.kinetic_energy / throw_ke_ref.mean:.1f} x")
console.print(f"  z-score above reference mean   : {throw_ke_ref.z(throw_r.kinetic_energy):.1f}")
console.print(f"  force required (Newton 2nd law): {throw_r.f_peak:,.0f} N")
console.print(f"  two-arm push budget (Daams 1994): {push_budget_two_arm:,.0f} N")
"""

VERDICT_EXPORT_CODE = """\
# Final verdict tally and export of the result table for the markdown report
verdict_counts = score_df["verdict"].value_counts().to_dict()
console.print("[bold]Verdict tally across all (phase, quantity) scores[/bold]")
for v in ("plausible", "strained", "implausible", "extreme"):
    console.print(f"  {v:14s}: {verdict_counts.get(v, 0)}")

implausible_or_worse = score_df[score_df["verdict"].isin(["implausible", "extreme"])]
console.print(f"\\n[bold]implausible or extreme phases (z > 2):[/bold] {len(implausible_or_worse)}")
console.print(implausible_or_worse[["phase", "quantity", "required", "ref_mean", "z", "verdict"]].to_string(index=False))

# Persist for the verdict report
score_df.to_csv(FIG_DIR.parent / "01-phase-scores.csv", index=False)
results_df.to_csv(FIG_DIR.parent / "01-phase-kinematics.csv", index=False)
"""

CLOSING_MD = """\
## Summary

Refer to `reports/corridor-plausibility.md` for the narrative verdict and embedded figures. The per-phase scores and kinematic table are written to `reports/01-phase-scores.csv` and `reports/01-phase-kinematics.csv` for downstream use.

### Limitations

- Constant-acceleration (triangular velocity) profile per phase is the most charitable interpretation; smoother profiles would require higher peaks.
- Resistance model is a friction-equivalent + constant brake; it does not capture active resistance (lowering centre of mass, bracing, counter-rotation).
- Reference distributions are normal with adult male means and SDs; tail probabilities should be read as approximate.
- The analysis is purely kinematic plausibility against population biomechanics. It does not constitute a forensic conclusion about any specific event.
"""


def build() -> None:
    nb = new_notebook()
    nb["cells"] = [
        new_markdown_cell(HEADER_MD),
        new_code_cell(IMPORTS_CODE),
        new_code_cell(SEED_CODE),
        new_markdown_cell("## Configuration"),
        new_code_cell(CONFIG_CODE),
        new_code_cell(GEOMETRY_FIG_CODE),
        new_markdown_cell("## Phase decomposition"),
        new_code_cell(PHASES_CODE),
        new_code_cell(TIMELINE_CODE),
        new_markdown_cell("## Kinematic demands per phase"),
        new_code_cell(KINEMATICS_CODE),
        new_code_cell(THROW_SANITY_CODE),
        new_code_cell(ACTOR_EFFORT_CODE),
        new_markdown_cell("## Reference distributions"),
        new_code_cell(REFERENCES_CODE),
        new_markdown_cell("## Plausibility scoring"),
        new_code_cell(SCORING_CODE),
        new_code_cell(PHASE_SUMMARY_CODE),
        new_code_cell(VERDICT_SUMMARY_CODE),
        new_markdown_cell("## Visualisations"),
        new_code_cell(DEMAND_PLOT_CODE),
        new_markdown_cell("## Time-series: speed, acceleration, force, impulse"),
        new_code_cell(TIMELINES_CODE),
        new_code_cell(REFERENCE_OVERLAY_CODE),
        new_markdown_cell("## Throw energy budget"),
        new_code_cell(ENERGY_BREAKDOWN_CODE),
        new_markdown_cell("## Verdict tally and export"),
        new_code_cell(VERDICT_EXPORT_CODE),
        new_markdown_cell(CLOSING_MD),
    ]

    # Attach kernel metadata (uv env registered as 'henryk-sim')
    nb["metadata"] = {
        "kernelspec": {
            "display_name": "Python [uv env:henryk-sim]",
            "language": "python",
            "name": "henryk-sim",
        },
        "language_info": {"name": "python"},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as f:
        nbformat.write(nb, f)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    build()
