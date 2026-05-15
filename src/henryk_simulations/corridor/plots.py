"""Matplotlib figures for the corridor analysis."""

from __future__ import annotations

from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from henryk_simulations.corridor.acoustics import (
    REF_SOUNDS as DEFAULT_REF_SOUNDS,
)
from henryk_simulations.corridor.acoustics import (
    AcousticPrediction,
)
from henryk_simulations.corridor.config import Scenario
from henryk_simulations.corridor.kinematics import G, PhaseResult
from henryk_simulations.corridor.plausibility import PlausibilityScore, Verdict
from henryk_simulations.corridor.references import Reference

SKILL_MPL_PALETTE = ["#3498DB", "#E74C3C", "#2ECC71"]  # primary / secondary / tertiary

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
    # Stagger the σ-band annotations vertically so adjacent labels don't
    # overlap, and place them in the headroom above the top data row.
    for i, (x, label, c) in enumerate(
        [
            (1, "1σ strained", VERDICT_COLORS[Verdict.STRAINED]),
            (2, "2σ implausible", VERDICT_COLORS[Verdict.IMPLAUSIBLE]),
            (3, "3σ extreme", VERDICT_COLORS[Verdict.EXTREME]),
        ]
    ):
        ax.axvline(x, color=c, linestyle="--", linewidth=0.8, alpha=0.7)
        ax.text(
            x + 0.04,
            len(df) + 0.15 + (i * 0.30),
            label,
            color=c,
            fontsize=8,
            ha="left",
            va="bottom",
        )
    ax.set_xlabel("z-score above reference mean")
    ax.set_title("Plausibility z-scores (higher = harder to satisfy)", pad=14)
    ax.grid(axis="x", linestyle=":", alpha=0.5)
    # Add room above the top data row so the 1σ/2σ/3σ legend labels don't
    # overlap the row labels.
    ax.set_ylim(-0.5, len(df) + 1.2)

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
    """Overhead schematic of the corrected two-segment corridor with actors and props.

    Layout convention matches references/incident/geometry.md:
    - Corridor runs W (left) to E (right)
    - Apartment door on N wall (top) of segment 2; elevator door on S wall
      (bottom) of segment 2, slightly west of the apartment door
    - Segment 1 is the narrower entrance to the west
    - V at apt door W envelope facing S; A pressed flat against elevator
      door facing N; Cecilia in segment 1 facing E
    - [Box] briefcase at E edge of elevator door; [Str] stroller in segment
      2 NW; D apartment-door panel swung W
    """
    fig, ax = plt.subplots(figsize=(10, 5.2))

    # Geometry (metres). Segment 1 is the western entrance (1.8 m long,
    # narrower); segment 2 is the wider eastern section containing the doors.
    # Segment 2 is at least 2x segment 1's length so Andrew/Victoria have room
    # to manoeuvre and the door swing + briefcase fit naturally.
    # The elbow (step in the wall) is on the SOUTH side: both segments share
    # the same N wall; segment 2's S wall is further south than segment 1's.
    seg1_w = 1.8
    seg2_w = 6.0
    seg1_height = 1.6  # corridor width N-S in segment 1
    seg2_height = 2.0  # segment 2 only ~0.4 m deeper to the S (shallow elbow)
    seg2_x0 = seg1_w
    total_w = seg1_w + seg2_w

    # Both segments share the N wall at y = +seg2_height/2.
    # Segment 1 S wall is less south; segment 2 S wall is further south.
    n_wall = seg2_height / 2
    s_seg1 = n_wall - seg1_height  # less negative (less south)
    s_seg2 = -seg2_height / 2  # more negative (further south)

    # Walls (drawn as thick lines)
    wall_kw = {"color": "#37474f", "linewidth": 3.0}
    apt_door_x = seg2_x0 + 2.0  # apt door centred 2.0 m into segment 2
    apt_door_w = 1.0  # 1 m wide
    # N wall of segment 2 (with apartment-door gap)
    ax.plot([0, apt_door_x - apt_door_w / 2], [n_wall, n_wall], **wall_kw)
    ax.plot([apt_door_x + apt_door_w / 2, total_w], [n_wall, n_wall], **wall_kw)
    # Segment 1 S wall (less south)
    ax.plot([0, seg2_x0], [s_seg1, s_seg1], **wall_kw)
    # Segment 2 S wall (further south)
    ax.plot([seg2_x0, total_w], [s_seg2, s_seg2], **wall_kw)
    # S elbow (step down from segment 1 south wall to segment 2 south wall)
    ax.plot([seg2_x0, seg2_x0], [s_seg1, s_seg2], **wall_kw)
    # W end wall
    ax.plot([0, 0], [s_seg1, n_wall], **wall_kw)
    # E end wall
    ax.plot([total_w, total_w], [s_seg2, n_wall], **wall_kw)

    # Apartment door (on N wall) - hinged at the EAST edge of the doorway,
    # swings into the corridor with the panel ending up south-west of the
    # hinge. The free end of the open door rests near the corridor floor at
    # the W edge of the original doorway opening.
    apt_door_hinge_x = apt_door_x + apt_door_w / 2
    door_swing_angle = 110  # measured from +x; panel mostly open, pointing SSW from E hinge
    angle_rad = np.deg2rad(door_swing_angle)
    door_panel_tip = (
        apt_door_hinge_x + apt_door_w * np.cos(angle_rad),
        n_wall - apt_door_w * np.sin(angle_rad),
    )
    door_panel = mpatches.Polygon(
        [
            (apt_door_hinge_x, n_wall),
            (apt_door_hinge_x + 0.05, n_wall - 0.05),
            (door_panel_tip[0] + 0.05, door_panel_tip[1] - 0.05),
            (door_panel_tip[0], door_panel_tip[1]),
        ],
        closed=True,
        color="#1565c0",
        alpha=0.7,
    )
    ax.add_patch(door_panel)
    ax.text(
        apt_door_x,
        n_wall + 0.15,
        "apartment door (hinges E, swings into corridor)",
        ha="center",
        fontsize=8,
        color="#1565c0",
    )

    # Elevator door (on S wall) - slightly west of the apartment door, on the
    # south side. The elevator door is visualised as a wide opening with the
    # door panel slid into the wall.
    elev_door_x = seg2_x0 + 1.3  # elevator door centred slightly west of apt
    elev_door_w = 1.2  # wider than the apt door
    ax.plot(
        [elev_door_x - elev_door_w / 2, elev_door_x + elev_door_w / 2],
        [s_seg2, s_seg2],
        color="#b71c1c",
        linewidth=6,
    )
    ax.text(
        elev_door_x,
        s_seg2 - 0.25,
        "elevator door",
        ha="center",
        fontsize=8,
        color="#b71c1c",
    )

    # Actors -----------------------------------------------------------------
    # V (Victoria): at apartment door W envelope (opposite the E hinge),
    # facing S (downward)
    v_xy = (apt_door_x - 0.15, n_wall - 0.18)
    v_circle = mpatches.Circle(
        v_xy, 0.18, color="#c45a3a", label=f"Victoria ({bodies.m_mass:.0f} kg)"
    )
    ax.add_patch(v_circle)
    ax.annotate(
        "",
        xy=(v_xy[0], v_xy[1] - 0.45),
        xytext=v_xy,
        arrowprops={"arrowstyle": "->", "color": "#c45a3a", "lw": 2.2},
    )
    ax.text(
        v_xy[0],
        v_xy[1],
        "V",
        ha="center",
        va="center",
        fontweight="bold",
        color="white",
        fontsize=10,
    )

    # A (Andrew): pressed flat against the elevator door, facing N (upward)
    a_xy = (elev_door_x, s_seg2 + 0.22)
    a_circle = mpatches.Circle(
        a_xy, 0.20, color="#5c8da7", label=f"Andrew ({bodies.h_mass:.0f} kg)"
    )
    ax.add_patch(a_circle)
    ax.annotate(
        "",
        xy=(a_xy[0], a_xy[1] + 0.55),
        xytext=a_xy,
        arrowprops={"arrowstyle": "->", "color": "#5c8da7", "lw": 2.2},
    )
    ax.text(
        a_xy[0],
        a_xy[1],
        "A",
        ha="center",
        va="center",
        fontweight="bold",
        color="white",
        fontsize=11,
    )

    # Cecilia: in segment 1, facing E (rightward)
    c_xy = (0.5, 0.0)
    c_circle = mpatches.Circle(c_xy, 0.15, color="#5b8d5b", label="Cecilia (court curator)")
    ax.add_patch(c_circle)
    ax.annotate(
        "",
        xy=(c_xy[0] + 0.55, c_xy[1]),
        xytext=c_xy,
        arrowprops={"arrowstyle": "->", "color": "#5b8d5b", "lw": 2.0},
    )
    ax.text(
        c_xy[0],
        c_xy[1],
        "C",
        ha="center",
        va="center",
        fontweight="bold",
        color="white",
        fontsize=10,
    )

    # Props ------------------------------------------------------------------
    # [Box] briefcase straddles the east edge of the elevator door (half on the
    # door panel, half past the door frame on the wall)
    box_w, box_h = 0.50, 0.30
    box_x = elev_door_x + elev_door_w / 2 - box_w / 2  # centred on east edge
    box_y = s_seg2 + 0.05
    briefcase = mpatches.Rectangle(
        (box_x, box_y),
        box_w,
        box_h,
        facecolor="#9e9e9e",
        edgecolor="#37474f",
        linewidth=1.2,
        label="[Box] aluminium briefcase",
    )
    ax.add_patch(briefcase)
    ax.text(
        box_x + box_w / 2,
        box_y + box_h / 2,
        "[Box]",
        ha="center",
        va="center",
        fontsize=7,
        color="#37474f",
    )

    # [Str] stroller in segment 2 NW
    str_x, str_y = seg2_x0 + 0.3, n_wall - 0.6
    stroller = mpatches.Rectangle(
        (str_x, str_y),
        0.45,
        0.35,
        facecolor="#fff59d",
        edgecolor="#a98e00",
        linewidth=1.2,
        label="[Str] baby stroller",
    )
    ax.add_patch(stroller)
    ax.text(
        str_x + 0.22, str_y + 0.17, "[Str]", ha="center", va="center", fontsize=7, color="#7a6700"
    )

    # Segment labels
    ax.text(
        seg2_x0 / 2,
        s_seg2 + 0.15,
        "segment 1\n(entrance)",
        ha="center",
        fontsize=8,
        color="#37474f",
        alpha=0.7,
    )
    ax.text(
        seg2_x0 + seg2_w / 2 + 0.5,
        s_seg2 + 0.18,
        "segment 2",
        ha="center",
        fontsize=8,
        color="#37474f",
        alpha=0.7,
    )

    # Cardinal-direction rosette (small inset, top-right corner, clear of walls)
    rose = ax.inset_axes([0.91, 0.76, 0.085, 0.18])
    rose.set_xlim(-1.25, 1.25)
    rose.set_ylim(-1.25, 1.25)
    rose.set_aspect("equal")
    rose.axis("off")
    # Outer circle (subtle)
    rose.add_patch(
        mpatches.Circle((0, 0), 1.0, fill=False, color="#37474f", linewidth=1.0, alpha=0.45)
    )
    # Four cardinal points drawn as elongated diamond petals (N/S long axis,
    # E/W short axis offset by 90 deg). Each petal is a 4-point polygon from
    # centre -> side -> tip -> side -> centre. N petal in solid colour to mark
    # primary heading; other three lighter for contrast.
    petal_long, petal_wide = 0.78, 0.18
    petals = [
        ((0, 1), "#37474f", 1.00),  # N (solid)
        ((0, -1), "#37474f", 0.55),  # S
        ((1, 0), "#37474f", 0.55),  # E
        ((-1, 0), "#37474f", 0.55),  # W
    ]
    for (ux, uy), color, alpha in petals:
        # tip at (ux*petal_long, uy*petal_long), sides perpendicular
        tip = (ux * petal_long, uy * petal_long)
        sideL = (-uy * petal_wide, ux * petal_wide)
        sideR = (uy * petal_wide, -ux * petal_wide)
        rose.add_patch(
            mpatches.Polygon(
                [(0, 0), sideL, tip, sideR],
                closed=True,
                color=color,
                alpha=alpha,
            )
        )
    # Centre dot
    rose.add_patch(mpatches.Circle((0, 0), 0.08, color="#37474f"))
    # Labels just outside the circle (a touch more spacing for breathing room)
    for (ux, uy), label in [((0, 1), "N"), ((0, -1), "S"), ((1, 0), "E"), ((-1, 0), "W")]:
        rose.text(
            ux * 1.20,
            uy * 1.20,
            label,
            ha="center",
            va="center",
            fontweight="bold",
            fontsize=8,
            color="#37474f",
        )

    # Distance annotation: 2 m N-S throw distance between doors
    ax.annotate(
        "",
        xy=(apt_door_x + 1.2, s_seg2 + 0.05),
        xytext=(apt_door_x + 1.2, n_wall - 0.05),
        arrowprops={"arrowstyle": "<->", "color": "#6a1b9a", "lw": 1.0},
    )
    ax.text(
        apt_door_x + 1.4,
        0,
        "~2 m\n(N-S throw\ndistance)",
        fontsize=8,
        color="#6a1b9a",
        va="center",
    )

    ax.set_xlim(-0.3, total_w + 0.4)
    ax.set_ylim(s_seg2 - 0.55, n_wall + 0.95)
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title(
        "Corridor geometry at the contested moment (top view)",
        pad=10,
    )
    ax.legend(loc="upper left", fontsize=8, framealpha=0.9)
    ax.grid(linestyle=":", alpha=0.3)
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
    """Shaded phase bands with inline phase labels.

    Labels sit at 90% of y_top, well above any data line given the 35%
    headroom in _plot_quantity_over_time.
    """
    for idx, (phase, start) in enumerate(zip(scenario.phases, scenario.phase_starts)):
        color = PHASE_PALETTE[idx % len(PHASE_PALETTE)]
        ax.axvspan(start, start + phase.duration, alpha=0.08, color=color, zorder=0)
        ax.text(
            start + phase.duration / 2,
            y_top * 0.90,
            f"{idx + 1}. {phase.name}",
            ha="center",
            va="top",
            fontsize=9,
            color="#37474f",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85, "pad": 2.0},
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
    # Headroom: leave ~35% above data peak so phase-band labels don't intersect
    # the data line.
    y_top = max(data_max, visible_refs_max) * 1.35
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


def plot_audio_signature(
    prediction: AcousticPrediction,
    *,
    ref_sounds: list[tuple[int, str]] | None = None,
    clip_threshold_db: float = 120.0,
    palette: list[str] | None = None,
    out_path: Path | None = None,
) -> plt.Figure:
    """SPL band chart per listener distance with reference-sound markers.

    Each listener (from `prediction.listeners`) gets a horizontal band spanning
    the SPL range across the radiation-efficiency bracket, with the typical
    value marked as a dot. Reference SPL benchmarks (gunshot, jackhammer,
    conversation, ...) are drawn as vertical tick lines, and the phone-mic
    clipping region above `clip_threshold_db` is shaded.
    """
    refs = ref_sounds if ref_sounds is not None else DEFAULT_REF_SOUNDS
    palette = palette if palette is not None else SKILL_MPL_PALETTE

    fig, ax = plt.subplots(figsize=(12, 5.4))

    # Reference benchmarks - vertical labels above the plot to avoid horizontal
    # overlap between adjacent SPL ticks (120/130/140 are only 10 dB apart).
    for db, txt in refs:
        ax.axvline(db, color="gray", alpha=0.35, linewidth=0.8, zorder=0)
        ax.text(
            db,
            1.02,
            f"{db} dB  {txt}",
            ha="left",
            va="center",
            fontsize=7,
            rotation=90,
            transform=ax.get_xaxis_transform(),
            color="dimgray",
        )

    # Clipping danger zone
    ax.axvspan(
        clip_threshold_db, 200, ymin=0, ymax=1, color=SKILL_MPL_PALETTE[1], alpha=0.07, zorder=0
    )
    ax.text(
        clip_threshold_db + 1,
        len(prediction.listeners) - 0.4,
        f"phone mic clips above ~{clip_threshold_db:.0f} dB SPL",
        color=SKILL_MPL_PALETTE[1],
        fontsize=9,
        fontweight="bold",
        va="top",
    )

    # Per-listener bands
    for y, (listener_label, _r) in enumerate(prediction.listeners):
        color = palette[y % len(palette)]
        spls = list(prediction.spl_grid[listener_label].values())
        spl_low, spl_high = min(spls), max(spls)
        # Typical value: middle of the configured eta range
        typical_label = list(prediction.eta_range)[len(prediction.eta_range) // 2]
        spl_typical = prediction.spl_grid[listener_label][typical_label]

        ax.barh(
            y,
            spl_high - spl_low,
            left=spl_low,
            height=0.55,
            color=color,
            alpha=0.5,
            edgecolor=color,
            linewidth=2,
        )
        ax.plot(spl_typical, y, "o", color="black", markersize=8, zorder=5)
        ax.text(
            spl_low - 1.5,
            y,
            listener_label,
            ha="right",
            va="center",
            fontsize=10,
            fontweight="bold",
        )
        ax.text(
            spl_high + 1.5,
            y,
            f"{spl_low:.0f} - {spl_high:.0f} dB SPL",
            ha="left",
            va="center",
            fontsize=9,
        )

    ax.set_yticks([])
    ax.set_xlim(50, 175)
    ax.set_ylim(-0.5, len(prediction.listeners) - 0.2)
    ax.set_xlabel("Sound pressure level (dB SPL re 20 µPa)")
    ax.set_title(
        "Predicted peak SPL of the elevator-door impact vs reference sounds",
        fontsize=12,
        fontweight="bold",
        pad=70,
    )
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    fig.subplots_adjust(top=0.74, bottom=0.13, left=0.04, right=0.96)
    if out_path is not None:
        fig.savefig(out_path, dpi=120, bbox_inches="tight")
    return fig


__all__ = [
    "PHASE_PALETTE",
    "SKILL_MPL_PALETTE",
    "VERDICT_COLORS",
    "plot_acceleration_over_time",
    "plot_arm_conflict",
    "plot_audio_signature",
    "plot_corridor_overhead",
    "plot_force_over_time",
    "plot_impulse_over_time",
    "plot_per_phase_demand",
    "plot_phase_timeline",
    "plot_reference_overlay",
    "plot_speed_over_time",
    "plot_verdict_summary",
]
