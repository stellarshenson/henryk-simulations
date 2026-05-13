"""Matplotlib figures for the corridor analysis."""

from __future__ import annotations

from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from henryk_simulations.corridor.config import Scenario
from henryk_simulations.corridor.kinematics import G, PhaseResult
from henryk_simulations.corridor.plausibility import PlausibilityScore, Verdict
from henryk_simulations.corridor.references import Reference

VERDICT_COLORS = {
    Verdict.PLAUSIBLE: "#3a8a3a",
    Verdict.STRAINED: "#d9a23a",
    Verdict.IMPLAUSIBLE: "#c45a3a",
    Verdict.EXTREME: "#8b1f1f",
}
PHASE_PALETTE = sns.color_palette("crest", 7)


def _verdict_color(v: Verdict) -> str:
    return VERDICT_COLORS[v]


def plot_phase_timeline(
    phases,
    phase_starts: list[float],
    *,
    total_time: float,
    out_path: Path | None = None,
    title: str = "Corridor phase timeline (3.0 s budget)",
) -> plt.Figure:
    """Horizontal gantt of phase windows. Overlapping phases drawn on a sub-row."""
    fig, ax = plt.subplots(figsize=(11, 3.5))
    for idx, (phase, start) in enumerate(zip(phases, phase_starts)):
        row = idx
        color = PHASE_PALETTE[idx % len(PHASE_PALETTE)]
        ax.broken_barh(
            [(start, phase.duration)],
            (row - 0.4, 0.8),
            facecolors=color,
            edgecolors="black",
            linewidth=0.8,
        )
        ax.text(
            start + phase.duration / 2,
            row,
            f"{phase.name}\n{phase.duration:.2f} s",
            ha="center",
            va="center",
            fontsize=9,
            color="white",
            fontweight="bold",
        )
        if phase.overlaps_with is not None:
            ax.annotate(
                "overlaps phase 4 (throw)",
                xy=(start + phase.duration / 2, row + 0.5),
                ha="center",
                fontsize=8,
                color="#555555",
            )
    ax.set_yticks(range(len(phases)))
    ax.set_yticklabels([f"{i + 1}. {p.name}" for i, p in enumerate(phases)])
    ax.invert_yaxis()
    ax.set_xlabel("time (s)")
    ax.set_xlim(0, total_time * 1.02)
    ax.axvline(total_time, color="black", linestyle="--", linewidth=1.0, alpha=0.6)
    ax.set_title(title)
    ax.grid(axis="x", linestyle=":", alpha=0.5)
    fig.tight_layout()
    if out_path is not None:
        fig.savefig(out_path, dpi=140, bbox_inches="tight")
    return fig


def plot_per_phase_demand(
    results_df: pd.DataFrame,
    *,
    columns: list[str],
    out_path: Path | None = None,
    title: str = "Per-phase kinematic demand (passive vs small-resistance)",
) -> plt.Figure:
    """Grouped bar chart of per-phase peak values (passive / no-resistance)."""
    fig, axes = plt.subplots(1, len(columns), figsize=(4.0 * len(columns), 4.5))
    if len(columns) == 1:
        axes = [axes]
    palette = {"passive": "#5c8da7"}
    for ax, col in zip(axes, columns):
        plot_df = results_df.copy()
        sns.barplot(
            data=plot_df,
            x="phase",
            y=col,
            hue="resistance",
            palette=palette,
            ax=ax,
            edgecolor="black",
        )
        ax.set_title(col)
        ax.set_xlabel("")
        ax.tick_params(axis="x", rotation=35)
        for label in ax.get_xticklabels():
            label.set_horizontalalignment("right")
        ax.grid(axis="y", linestyle=":", alpha=0.5)
    fig.suptitle(title, fontsize=13)
    fig.tight_layout()
    if out_path is not None:
        fig.savefig(out_path, dpi=140, bbox_inches="tight")
    return fig


def plot_reference_overlay(
    scores: list[PlausibilityScore],
    references: list[Reference],
    *,
    out_path: Path | None = None,
    title: str = "Required values against reference distributions",
) -> plt.Figure:
    """One distribution per reference with vertical lines for each phase demand."""
    n = len(references)
    cols = 2
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(11, 3.5 * rows))
    axes = np.atleast_1d(axes).flatten()
    for ax, ref in zip(axes, references):
        ci_lo, ci_hi = ref.ci(0.95)
        x = np.linspace(ref.mean - 4 * ref.sd, ref.mean + 4 * ref.sd, 500)
        y = ref.distribution.pdf(x)
        ax.fill_between(x, y, color="#cfd8dc", alpha=0.6, label="reference PDF")
        ax.axvline(ref.mean, color="#37474f", linestyle="-", linewidth=1.5, label="mean")
        ax.axvspan(ci_lo, ci_hi, color="#37474f", alpha=0.10, label="95% CI")

        matching = [s for s in scores if s.reference_name == ref.name]
        for s in matching:
            color = _verdict_color(s.verdict)
            ax.axvline(s.required_value, color=color, linestyle="--", linewidth=2)
            ax.text(
                s.required_value,
                ax.get_ylim()[1] * 0.92,
                f"{s.phase_name}\nz={s.z:.1f}",
                color=color,
                ha="center",
                fontsize=8,
                rotation=0,
                bbox={"facecolor": "white", "edgecolor": color, "alpha": 0.85, "pad": 2},
            )
        ax.set_title(f"{ref.name}\n[{ref.units}]", fontsize=10)
        ax.set_xlabel(ref.units)
        ax.set_ylabel("density")
        ax.grid(linestyle=":", alpha=0.5)
        ax.legend(loc="upper right", fontsize=7)
    for ax in axes[len(references) :]:
        ax.set_visible(False)
    fig.suptitle(title, fontsize=13)
    fig.tight_layout()
    if out_path is not None:
        fig.savefig(out_path, dpi=140, bbox_inches="tight")
    return fig


def plot_arm_conflict(
    throw_result: PhaseResult,
    reach_result: PhaseResult,
    *,
    out_path: Path | None = None,
) -> plt.Figure:
    """Phase 4 vs phase 5 - same arms perform throw and neck-reach simultaneously."""
    fig, ax = plt.subplots(figsize=(9, 4.5))
    items = [
        ("Throw - 70 kg body to 5.7 m/s", throw_result.f_peak, "#5c8da7"),
        ("Two-arm budget at 800 N two-arm push", 800.0, "#cfd8dc"),
        ("Neck-reach hands to 3.5 m/s", reach_result.reach_f_peak, "#c45a3a"),
    ]
    labels = [name for name, _, _ in items]
    values = [v for _, v, _ in items]
    colors = [c for _, _, c in items]
    bars = ax.barh(labels, values, color=colors, edgecolor="black")
    for bar, val in zip(bars, values):
        ax.text(
            val + 30,
            bar.get_y() + bar.get_height() / 2,
            f"{val:,.0f} N",
            va="center",
            fontsize=10,
        )
    ax.set_xlabel("force (N)")
    ax.set_title(
        "Phase 4 + 5 conflict: throw force vs two-arm budget vs reach demand",
        fontsize=12,
    )
    ax.grid(axis="x", linestyle=":", alpha=0.5)
    fig.tight_layout()
    if out_path is not None:
        fig.savefig(out_path, dpi=140, bbox_inches="tight")
    return fig


def plot_verdict_summary(
    scores: list[PlausibilityScore],
    *,
    out_path: Path | None = None,
) -> plt.Figure:
    """Lollipop chart of z-scores by (phase, quantity) coloured by verdict."""
    df = pd.DataFrame(
        [
            {
                "phase": s.phase_name,
                "quantity": s.quantity_label,
                "z": s.z,
                "verdict": s.verdict.value,
                "label": f"{s.phase_name} - {s.quantity_label}",
            }
            for s in scores
        ],
    ).sort_values("z")
    fig, ax = plt.subplots(figsize=(10, max(4, 0.35 * len(df))))
    ys = np.arange(len(df))
    colors = [_verdict_color(Verdict(v)) for v in df["verdict"]]
    ax.hlines(ys, 0, df["z"], colors=colors, linewidth=3)
    ax.plot(df["z"], ys, "o", color="black", markersize=6)
    for y, z, col in zip(ys, df["z"], colors):
        ax.text(z + (0.15 if z >= 0 else -0.15), y, f"{z:.1f}σ", va="center", fontsize=8)
    ax.set_yticks(ys)
    ax.set_yticklabels(df["label"])
    ax.axvline(0, color="black", linewidth=0.8)
    for x, label, c in [
        (1, "1σ strained", VERDICT_COLORS[Verdict.STRAINED]),
        (2, "2σ implausible", VERDICT_COLORS[Verdict.IMPLAUSIBLE]),
        (3, "3σ extreme", VERDICT_COLORS[Verdict.EXTREME]),
    ]:
        ax.axvline(x, color=c, linestyle="--", linewidth=0.8, alpha=0.7)
        ax.text(x, len(df) - 0.5, label, color=c, fontsize=8, ha="left")
    ax.set_xlabel("z-score above reference mean")
    ax.set_title("Plausibility z-scores (higher = harder to satisfy)")
    ax.grid(axis="x", linestyle=":", alpha=0.5)

    handles = [
        mpatches.Patch(color=VERDICT_COLORS[v], label=v.value)
        for v in [Verdict.PLAUSIBLE, Verdict.STRAINED, Verdict.IMPLAUSIBLE, Verdict.EXTREME]
    ]
    ax.legend(handles=handles, loc="lower right", fontsize=8)
    fig.tight_layout()
    if out_path is not None:
        fig.savefig(out_path, dpi=140, bbox_inches="tight")
    return fig


def plot_corridor_overhead(
    geometry,
    bodies,
    *,
    out_path: Path | None = None,
) -> plt.Figure:
    """Overhead schematic of the corridor with both bodies at phase 0."""
    fig, ax = plt.subplots(figsize=(8, 4))
    w = geometry.corridor_width
    lat = geometry.corridor_lateral
    # corridor walls (top and bottom)
    ax.fill_between([0, w], lat / 2, lat / 2 + 0.05, color="#37474f")
    ax.fill_between([0, w], -lat / 2 - 0.05, -lat / 2, color="#37474f")
    # apartment door at x=0
    ax.plot([0, 0], [-0.45, 0.45], color="#1565c0", linewidth=5)
    ax.text(-0.1, 0, "apartment\ndoor", ha="right", va="center", fontsize=9, color="#1565c0")
    # elevator door at x=w
    ax.plot([w, w], [-0.45, 0.45], color="#b71c1c", linewidth=5)
    ax.text(w + 0.05, 0, "elevator\ndoor", ha="left", va="center", fontsize=9, color="#b71c1c")
    # bodies (initial positions per phase 1 start)
    h = mpatches.Circle((0.35, 0.0), 0.25, color="#5c8da7", label=f"Andrew ({bodies.h_mass} kg)")
    m = mpatches.Circle((0.15, 0.0), 0.22, color="#c45a3a", label=f"Victoria ({bodies.m_mass} kg)")
    ax.add_patch(h)
    ax.add_patch(m)
    ax.text(0.35, 0.45, "H", ha="center", fontsize=9)
    ax.text(0.15, 0.45, "M", ha="center", fontsize=9)
    ax.set_xlim(-0.5, w + 0.5)
    ax.set_ylim(-lat / 2 - 0.2, lat / 2 + 0.4)
    ax.set_aspect("equal")
    ax.set_xlabel("x (m), apartment-door to elevator-door axis")
    ax.set_title(f"Corridor geometry, top view ({w:.1f} m wide)")
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    if out_path is not None:
        fig.savefig(out_path, dpi=140, bbox_inches="tight")
    return fig


def _triangle_v_profile(v_peak: float, t_local: np.ndarray, t_total: float) -> np.ndarray:
    """Triangular speed profile peaking at v_peak at t_total/2."""
    return np.where(
        t_local < t_total / 2,
        2 * v_peak * t_local / t_total,
        2 * v_peak * (1 - t_local / t_total),
    )


def _build_time_series(
    scenario: Scenario,
    results: list[PhaseResult],
    quantity: str,
    dt: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build per-body time series for one of: a, v, F, p (impulse cumulative).

    Profiles within a phase:
      - acceleration: |a| = a_peak constant (sign flips at midpoint, magnitude flat)
      - speed: triangular peak at midpoint
      - force: |F| = F_peak constant (Newton's 2nd, same shape as a)
      - impulse: cumulative integral of |F| over time
    """
    starts = scenario.phase_starts
    end_time = scenario.total_time
    t = np.arange(0, end_time + dt / 2, dt)
    h = np.zeros_like(t)
    m = np.zeros_like(t)
    h_acc = 0.0  # cumulative impulse trackers
    m_acc = 0.0
    for phase, start, r in zip(scenario.phases, starts, results):
        if phase.kind != "translate" or r.a_peak <= 0:
            continue
        in_phase = (t >= start - 1e-9) & (t <= start + phase.duration + 1e-9)
        t_local = t[in_phase] - start
        if quantity == "a":
            value = np.full_like(t_local, r.a_peak)
        elif quantity == "v":
            value = _triangle_v_profile(r.v_peak, t_local, phase.duration)
        elif quantity == "F":
            value = np.full_like(t_local, r.f_peak)
        elif quantity == "p":
            # Cumulative impulse: integrate |F| dt within phase
            value = r.f_peak * t_local
        else:
            raise ValueError(f"unknown quantity {quantity}")

        if phase.body == "M":
            m[in_phase] = value if quantity != "p" else m_acc + value
            if quantity == "p":
                m_acc += r.f_peak * phase.duration
                m[t > start + phase.duration + 1e-9] = m_acc
        elif phase.body == "H":
            h[in_phase] = value if quantity != "p" else h_acc + value
            if quantity == "p":
                h_acc += r.f_peak * phase.duration
                h[t > start + phase.duration + 1e-9] = h_acc
    return t, h, m


def _draw_phase_bands(
    ax: plt.Axes,
    scenario: Scenario,
    *,
    y_top: float,
) -> None:
    """Shaded phase bands with inline phase labels."""
    for idx, (phase, start) in enumerate(zip(scenario.phases, scenario.phase_starts)):
        color = PHASE_PALETTE[idx % len(PHASE_PALETTE)]
        ax.axvspan(start, start + phase.duration, alpha=0.08, color=color, zorder=0)
        ax.text(
            start + phase.duration / 2,
            y_top * 0.95,
            f"{idx + 1}. {phase.name}",
            ha="center",
            va="top",
            fontsize=9,
            color="#37474f",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.75, "pad": 1.5},
        )


def _plot_quantity_over_time(
    scenario: Scenario,
    results: list[PhaseResult],
    *,
    quantity: str,
    ylabel: str,
    title: str,
    refs: list[tuple[float, str, str]] | None = None,
    secondary_axis: tuple[str, float] | None = None,
    dt: float = 0.005,
    out_path: Path | None = None,
) -> plt.Figure:
    """Shared helper for the a(t), v(t), F(t), p(t) time-series plots."""
    t, h, m = _build_time_series(scenario, results, quantity, dt)
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(t, h, color="#5c8da7", linewidth=2.4, label="Andrew")
    ax.plot(t, m, color="#c45a3a", linewidth=2.4, label="Victoria")
    ax.fill_between(t, 0, h, color="#5c8da7", alpha=0.18)
    ax.fill_between(t, 0, m, color="#c45a3a", alpha=0.18)

    data_max = max(np.max(h), np.max(m))
    visible_refs_max = max((rv for rv, _, _ in refs or [] if rv <= data_max * 2.5), default=0.0)
    y_top = max(data_max, visible_refs_max) * 1.18
    if y_top <= 0:
        y_top = 1.0
    _draw_phase_bands(ax, scenario, y_top=y_top)

    if refs:
        for ref_value, ref_label, ref_color in refs:
            if ref_value > y_top:
                continue
            ax.axhline(ref_value, color=ref_color, linestyle=":", linewidth=1.0, alpha=0.85)
            ax.text(
                scenario.total_time,
                ref_value,
                f" {ref_label}",
                va="center",
                color=ref_color,
                fontsize=8,
            )

    ax.set_xlim(0, scenario.total_time * 1.18)
    ax.set_ylim(0, y_top)
    ax.set_xlabel("time (s)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(linestyle=":", alpha=0.5)

    if secondary_axis is not None:
        label, factor = secondary_axis
        secax = ax.secondary_yaxis(
            "right", functions=(lambda y, f=factor: y / f, lambda yg, f=factor: yg * f)
        )
        secax.set_ylabel(label)

    fig.tight_layout()
    if out_path is not None:
        fig.savefig(out_path, dpi=140, bbox_inches="tight")
    return fig


def plot_speed_over_time(
    scenario: Scenario,
    results: list[PhaseResult],
    *,
    out_path: Path | None = None,
) -> plt.Figure:
    """v(t) for both bodies. Triangular within each translation phase."""
    return _plot_quantity_over_time(
        scenario,
        results,
        quantity="v",
        ylabel="|v| (m/s)",
        title="|v(t)| linear speed over the 3.0 s budget",
        refs=[
            (1.4, "average walking 1.4 m/s", VERDICT_COLORS[Verdict.PLAUSIBLE]),
            (10.0, "elite 100m sprint peak 10 m/s", VERDICT_COLORS[Verdict.IMPLAUSIBLE]),
        ],
        out_path=out_path,
    )


def plot_force_over_time(
    scenario: Scenario,
    results: list[PhaseResult],
    *,
    out_path: Path | None = None,
) -> plt.Figure:
    """F(t) applied to the driven body in each translation phase."""
    return _plot_quantity_over_time(
        scenario,
        results,
        quantity="F",
        ylabel="|F| (N)",
        title="|F(t)| applied force over the 3.0 s budget",
        refs=[
            (400, "single-arm peak push 400 N", VERDICT_COLORS[Verdict.PLAUSIBLE]),
            (800, "two-arm peak push 800 N", VERDICT_COLORS[Verdict.STRAINED]),
            (1200, "elite two-arm 1200 N", VERDICT_COLORS[Verdict.IMPLAUSIBLE]),
        ],
        out_path=out_path,
    )


def plot_impulse_over_time(
    scenario: Scenario,
    results: list[PhaseResult],
    *,
    out_path: Path | None = None,
) -> plt.Figure:
    """Cumulative impulse |p(t)| delivered to each body over the 3.0 s budget."""
    return _plot_quantity_over_time(
        scenario,
        results,
        quantity="p",
        ylabel="cumulative impulse (N·s)",
        title="∫|F| dt cumulative impulse delivered to each body",
        out_path=out_path,
    )


def plot_acceleration_over_time(
    scenario: Scenario,
    results: list[PhaseResult],
    *,
    dt: float = 0.005,
    out_path: Path | None = None,
    title: str = "|a(t)| absolute linear acceleration over the 3.0 s budget",
    show_g_axis: bool = True,
) -> plt.Figure:
    """Plot absolute linear-acceleration magnitude versus time for H and M.

    Triangular velocity profile assumed: |a| is constant at a_peak through
    each translation phase (sign flips at the midpoint). The plot therefore
    looks like a step function whose envelope is the per-phase a_peak.

    Rotation and reach phases are not linear translations - shown as faint
    overlays so the viewer sees that those bodies are doing other work.
    """
    starts = scenario.phase_starts
    end_time = scenario.total_time
    t = np.arange(0, end_time + dt / 2, dt)
    a_h = np.zeros_like(t)
    a_m = np.zeros_like(t)
    for phase, start, r in zip(scenario.phases, starts, results):
        in_phase = (t >= start - 1e-9) & (t <= start + phase.duration + 1e-9)
        if phase.kind != "translate" or r.a_peak <= 0:
            continue
        if phase.body in ("M", "both"):
            a_m[in_phase] = np.maximum(a_m[in_phase], r.a_peak)
        if phase.body in ("H", "both"):
            a_h[in_phase] = np.maximum(a_h[in_phase], r.a_peak)

    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(t, a_h, color="#5c8da7", linewidth=2.4, label="Andrew |a(t)|")
    ax.plot(t, a_m, color="#c45a3a", linewidth=2.4, label="Victoria |a(t)|")
    ax.fill_between(t, 0, a_h, color="#5c8da7", alpha=0.18)
    ax.fill_between(t, 0, a_m, color="#c45a3a", alpha=0.18)

    # Phase band shading + labels
    y_top = max(np.max(a_h), np.max(a_m), G * 1.2) * 1.18
    for idx, (phase, start) in enumerate(zip(scenario.phases, starts)):
        color = PHASE_PALETTE[idx % len(PHASE_PALETTE)]
        ax.axvspan(start, start + phase.duration, alpha=0.06, color=color, zorder=0)
        ax.text(
            start + phase.duration / 2,
            y_top * 0.95,
            f"{idx + 1}\n{phase.name}",
            ha="center",
            va="top",
            fontsize=8,
            color="#37474f",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.7, "pad": 1.5},
        )

    # 1g reference line and selected biomech bands
    ax.axhline(G, color="#37474f", linestyle="--", linewidth=1.0, alpha=0.7)
    ax.text(end_time, G, " 1 g", va="center", color="#37474f", fontsize=8)
    ax.axhline(3.0, color=VERDICT_COLORS[Verdict.STRAINED], linestyle=":", linewidth=1.0)
    ax.text(
        end_time,
        3.0,
        " recreational sprint mean (3.0 m/s²)",
        va="center",
        color=VERDICT_COLORS[Verdict.STRAINED],
        fontsize=8,
    )
    ax.axhline(5.0, color=VERDICT_COLORS[Verdict.IMPLAUSIBLE], linestyle=":", linewidth=1.0)
    ax.text(
        end_time,
        5.0,
        " elite sprint mean (5.0 m/s²)",
        va="center",
        color=VERDICT_COLORS[Verdict.IMPLAUSIBLE],
        fontsize=8,
    )

    ax.set_xlim(0, end_time * 1.18)
    ax.set_ylim(0, y_top)
    ax.set_xlabel("time (s)")
    ax.set_ylabel("|a| (m/s²)")
    ax.set_title(title)
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(linestyle=":", alpha=0.5)

    if show_g_axis:
        secax = ax.secondary_yaxis("right", functions=(lambda y: y / G, lambda yg: yg * G))
        secax.set_ylabel("|a| (g)")

    fig.tight_layout()
    if out_path is not None:
        fig.savefig(out_path, dpi=140, bbox_inches="tight")
    return fig


__all__ = [
    "PHASE_PALETTE",
    "VERDICT_COLORS",
    "plot_acceleration_over_time",
    "plot_arm_conflict",
    "plot_corridor_overhead",
    "plot_force_over_time",
    "plot_impulse_over_time",
    "plot_per_phase_demand",
    "plot_phase_timeline",
    "plot_reference_overlay",
    "plot_speed_over_time",
    "plot_verdict_summary",
]
