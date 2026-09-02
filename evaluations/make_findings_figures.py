"""Generate the bar charts for ACE2.2-vs-ACE2.1-findings.md.

Numbers are transcribed from the wandb runs named in the report's appendix, so figures can
be regenerated without re-querying. Run:  python evaluations/make_findings_figures.py

Aggregation, which matters: each model's score is the MEDIAN over fields of that field's
error divided by the P1 three-seed mean for the same field. Per-field ratios are
dimensionless, so fields with different units can be combined; the median resists the few
fields where a normalised error is enormous because the field's own variability is tiny.
The top model layer is excluded throughout -- ACE has a known moisture-drift problem there,
and an unweighted mean over normalised errors is dominated by it (ACE2.2's
specific_total_water_0 alone is 4.3x ACE2.1's, which reverses the sign of the headline).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)

TEAL, RUST, INDIGO, OLIVE = "#00897B", "#C04E20", "#3A54B8", "#8F7B05"
INK, MUTED, GRID, SURFACE, BAND = "#14201E", "#5C6B68", "#DFE3E1", "#FCFCFB", "#E8EFEE"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "font.family": "DejaVu Sans", "font.size": 10,
    "text.color": INK, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.edgecolor": GRID, "axes.linewidth": 0.8,
})

def style(ax, xlabel=None, title=None, subtitle=None):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.xaxis.grid(True, color=GRID, lw=0.8)
    ax.yaxis.grid(False)
    ax.set_axisbelow(True)
    if xlabel: ax.set_xlabel(xlabel, color=MUTED, fontsize=9)
    if title: ax.set_title(title, loc="left", fontsize=12.5, color=INK, pad=16 if subtitle else 8)
    if subtitle:
        ax.text(0, 1.03, subtitle, transform=ax.transAxes, fontsize=9, color=MUTED, va="bottom")

MODELS = ["ACE2.1", "ACE2.2", "P1 seed 0", "P1 seed 1", "P1 seed 2", "P2"]
COLORS = [INDIGO, RUST, TEAL, TEAL, TEAL, OLIVE]

def ratio_chart(vals, spread, fname, title, subtitle, xlabel):
    fig, ax = plt.subplots(figsize=(8.2, 4.0))
    y = np.arange(len(MODELS))[::-1]
    lo, hi = spread
    ax.axvspan(lo, hi, color=BAND, zorder=0)
    ax.axvline(1.0, color=MUTED, lw=1, zorder=1)
    bars = ax.barh(y, vals, height=0.62, color=COLORS, zorder=2)
    for b in bars: b.set_linewidth(0)
    ax.set_yticks(y); ax.set_yticklabels(MODELS, fontsize=10, color=INK)
    ax.set_xlim(0, max(vals) * 1.2)
    for b, v in zip(bars, vals):
        ax.text(v + max(vals)*0.012, b.get_y()+b.get_height()/2, f"{v:.3f}",
                va="center", fontsize=9, color=INK)
    ax.text(hi, len(MODELS)-0.35, " range across P1's seeds", fontsize=8.5, color=MUTED, va="center")
    style(ax, xlabel, title, subtitle)
    fig.tight_layout(); fig.savefig(OUT/fname, dpi=200); plt.close(fig)

# fig 1 -- time-mean error (E1-like), 24 fields
ratio_chart([1.121, 0.977, 1.002, 0.879, 1.088, 0.954], (0.879, 1.088),
            "fig1-overall-skill.png",
            "Time-mean error over 1979-2014",
            "Relative to the P1 three-seed average. Below 1.0 is better; 24 fields.",
            "median per-field error ratio  (1.0 = same as P1 average)")

# fig 2 -- annual-mean error (E2-like), 25 fields
ratio_chart([0.982, 0.956, 0.980, 1.013, 0.953, 0.954], (0.953, 1.013),
            "fig2-annual-error.png",
            "Year-to-year and long-term error over 1979-2014",
            "Error of the annual-mean series, which carries the trend. 25 fields.",
            "median per-field error ratio  (1.0 = same as P1 average)")

# fig 3 -- the near-surface penalty, measured two independent ways against ACE2.2:
# P2 (built to reproduce ACE2.1's treatment) and ACE2.1 itself, from long36-ace21-plevft.
fields = ["2 m temperature", "2 m humidity", "10 m eastward wind", "10 m northward wind"]
p2_pct = [131.6, 242.3, 67.1, 119.5]
a21_pct = [155.7, 209.9, 78.7, 143.4]
fig, ax = plt.subplots(figsize=(8.4, 3.9))
y = np.arange(len(fields))[::-1]
h = 0.34
b1 = ax.barh(y + h/2, p2_pct, height=h, color=OLIVE, label="P2  (our variant)")
b2 = ax.barh(y - h/2, a21_pct, height=h, color=INDIGO, label="ACE2.1  (the real model)")
for bars in (b1, b2):
    for b in bars: b.set_linewidth(0)
ax.set_yticks(y); ax.set_yticklabels(fields, fontsize=10, color=INK)
ax.set_xlim(0, max(max(p2_pct), max(a21_pct)) * 1.18)
for bars, vals in ((b1, p2_pct), (b2, a21_pct)):
    for b, v in zip(bars, vals):
        ax.text(v + max(a21_pct)*0.012, b.get_y()+b.get_height()/2, f"+{v:.0f}%",
                va="center", fontsize=9, color=INK)
ax.legend(loc="lower right", frameon=False, fontsize=9)
style(ax, "how much worse than ACE2.2  (0% would mean no difference)",
      "Cost of predicting near-surface fields indirectly",
      "Both reconstruct these four fields instead of evolving them. P2 lands on ACE2.1 "
      "to within 10%.")
fig.tight_layout(); fig.savefig(OUT/"fig3-near-surface-penalty.png", dpi=200); plt.close(fig)

# fig 4 -- seed spread, the two recipes side by side (a null result)
a21 = [1.219, 1.113, 0.984, 1.064]
p1  = [0.918, 0.787, 0.985]
fig, ax = plt.subplots(figsize=(8.2, 3.2))
for i, (v, c, lab) in enumerate([(a21, INDIGO, "ACE2.1  (4 seeds)"), (p1, TEAL, "P1  (3 seeds)")]):
    yy = 1 - i
    ax.plot([min(v), max(v)], [yy, yy], color=c, lw=2.5, solid_capstyle="round", alpha=0.35)
    ax.scatter(v, [yy]*len(v), s=90, color=c, zorder=3, edgecolor=SURFACE, linewidth=2)
    ax.text(max(v) + 0.02, yy, f"spread {np.std(v, ddof=1)/np.mean(v)*100:.0f}% of its mean",
            va="center", fontsize=9, color=MUTED)
    ax.text(0.70, yy, lab, va="center", ha="right", fontsize=10, color=INK)
ax.set_yticks([]); ax.set_ylim(-0.6, 1.6); ax.set_xlim(0.70, 1.45)
style(ax, "median per-field error ratio, each seed scored against the seven-model average",
      "Does the random seed matter more in the newer recipe?",
      "Each dot is one seed. The two spreads are indistinguishable (p = 0.69).")
fig.tight_layout(); fig.savefig(OUT/"fig4-seed-spread.png", dpi=200); plt.close(fig)

# fig 5 -- the top-layer drift, and how much it varies by seed
groups = ["top-of-model\nhumidity", "top-of-model\neastward wind", "lowest layer\nhumidity"]
series = {
    "ACE2.1":   [0.0795, 0.0369, 0.0176],
    "ACE2.2":   [0.3440, 0.1406, 0.0118],
    "P1 seed 0":[0.2413, 0.1560, 0.0176],
    "P1 seed 1":[0.1173, 0.0400, 0.0122],
    "P1 seed 2":[0.0793, 0.0667, 0.0167],
}
cols = {"ACE2.1": INDIGO, "ACE2.2": RUST, "P1 seed 0": TEAL, "P1 seed 1": TEAL, "P1 seed 2": TEAL}
fig, axes = plt.subplots(1, 3, figsize=(8.6, 3.4))
for ax, gi, gname in zip(axes, range(3), groups):
    names = list(series)
    v = [series[n][gi] for n in names]
    x = np.arange(len(names))
    bars = ax.bar(x, v, width=0.66, color=[cols[n] for n in names])
    for b in bars: b.set_linewidth(0)
    ax.axhline(series["ACE2.1"][gi], color=MUTED, lw=1, ls=(0, (3, 3)), zorder=3)
    ax.set_xticks(x); ax.set_xticklabels(["2.1", "2.2", "rs0", "rs1", "rs2"], fontsize=8.5, color=MUTED)
    ax.set_title(gname, fontsize=9.5, color=INK, loc="left", pad=6)
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    ax.spines["left"].set_color(GRID); ax.yaxis.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    ax.tick_params(axis="y", labelsize=8.5)
axes[0].set_ylabel("normalised time-mean error", fontsize=9, color=MUTED)
fig.suptitle("Drift at the top of the model, and how much the seed changes it",
             x=0.008, ha="left", fontsize=12.5, color=INK, y=0.995)
fig.text(0.008, 0.90, "Dashed line is ACE2.1. The lowest layer, for contrast, is stable across all five.",
         fontsize=9, color=MUTED, ha="left")
fig.tight_layout(rect=(0, 0, 1, 0.87))
fig.savefig(OUT/"fig5-top-layer-drift.png", dpi=200); plt.close(fig)

# fig 6 -- the familiar view: global-mean 2 m temperature, year by year, in-sample.
# Series come from figures/annual_TMP2m.npz, extracted from the runs' own wandb `annual`
# plotly artifacts by fetch_annual_series.py -- the same rollouts as every other figure
# here, so unlike the production simulations these carry no forcing-convention offset.
_d = np.load(OUT / "annual_TMP2m.npz", allow_pickle=True)
yr, tgt = _d["year"], _d["target"]
p1 = np.vstack([_d[f"P1 seed {i}"] for i in range(3)])

fig, ax = plt.subplots(figsize=(8.8, 4.4))
ax.fill_between(yr, p1.min(0), p1.max(0), color=TEAL, alpha=0.18, lw=0,
                label="P1 (3 seeds, range)")
ax.plot(yr, p1.mean(0), color=TEAL, lw=2, solid_capstyle="round")
ax.plot(yr, _d["P2"], color=OLIVE, lw=1.6, solid_capstyle="round", label="P2")
ax.plot(yr, _d["ACE2.1"], color=INDIGO, lw=1.6, solid_capstyle="round", label="ACE2.1")
ax.plot(yr, _d["ACE2.2"], color=RUST, lw=1.6, solid_capstyle="round", label="ACE2.2")
ax.plot(yr, tgt, color=INK, lw=2.4, solid_capstyle="round", label="ERA5 (observed)")

# trend lines, drawn faint, for the reanalysis and the two submitted generations only
for v, col in ((tgt, INK), (_d["ACE2.2"], RUST), (_d["ACE2.1"], INDIGO)):
    fit = np.poly1d(np.polyfit(yr, v, 1))
    ax.plot(yr, fit(yr), color=col, lw=1, ls=(0, (4, 3)), alpha=0.75)

ax.set_xlim(yr[0] - 0.5, yr[-1] + 0.5)
ax.set_xticks([1980, 1985, 1990, 1995, 2000, 2005, 2010, 2014])
for sp in ("top", "right"): ax.spines[sp].set_visible(False)
ax.spines["left"].set_color(GRID); ax.spines["bottom"].set_color(GRID)
ax.yaxis.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
ax.set_ylabel("global-mean 2 m temperature (K)", fontsize=9, color=MUTED)
ax.set_xlabel("year", fontsize=9, color=MUTED)
ax.legend(frameon=False, loc="upper left", fontsize=9, ncol=2)
ax.set_title("Global-mean temperature, year by year, 1979-2014", loc="left",
             fontsize=12.5, color=INK, pad=26)
ax.text(0, 1.02, "Every model warms too slowly. Dashed lines are the fitted trends (values in the text).",
        transform=ax.transAxes, fontsize=9, color=MUTED, va="bottom")
fig.tight_layout(); fig.savefig(OUT/"fig6-tas-timeseries.png", dpi=200); plt.close(fig)

print("wrote:", *sorted(p.name for p in OUT.glob("*.png")))
