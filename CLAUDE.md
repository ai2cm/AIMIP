# CLAUDE.md — AIMIP project guidance

## Notebook Execution

When iterating on figures, run any cell that is solely involved in generating figures (function definitions, plot calls, helper utilities). **Never run the full notebook** — data processing takes ~20 minutes. Data is cached and already loaded in the kernel, so figure cells run immediately.

Typical pattern: edit the figure function cell → run it → run the call cell → inspect the output → repeat.

## Manuscript Figure Conventions

Rules established while building E1 manuscript figures. Apply to all notebooks (E2–E5).

### Labels and titles
- Use long names from xarray variable metadata (`da.attrs.get('long_name', varname)`), lowercased (`.lower()`), with underscores replaced by spaces.
- Exception: `zg` should be prefixed with "500 hPa" since the dataset metadata doesn't include the pressure level.
- For pressure-level panels in multi-panel figures, put the variable name on line 1, the pressure level (e.g. "850 hPa") on line 2, and units on the last line — always use consistent multi-line titles across all panels in a row to avoid vertical misalignment.
- Wrap long variable names with `textwrap.fill(long_name, width=18)` to prevent column-to-column title overprinting.
- Never put units in the y-axis ylabel if it risks overprinting adjacent panels — put units in the panel title instead (e.g. last line of a 2–3 line title).
- Use `labelpad=1` on ylabels to keep them tight to the tick labels.

### Scientific notation
- Never use matplotlib's default floating offset label (`1e-6` hovering above an axis) — it collides with titles and legends.
- Use `ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:g}'))` for all axes.
- Do NOT use `ScalarFormatter` — it still produces a floating multiplier label.

### Unit conversions
- Convert precipitation (`pr`) from kg m⁻² s⁻¹ to mm day⁻¹ by multiplying by 86400. Display units as `mm day$^{-1}$`.
- Apply scale factors to the data before plotting, not after.

### Pressure-level selection
- When selecting a single pressure level with `.sel(plev=plev)`, always chain `.drop_vars('plev')` immediately after. The scalar `plev` coordinate otherwise gets included in the DataFrame MultiIndex, causing the pressure value (e.g. 85000) to be plotted instead of the actual data.

### Maps
- Do not show coastlines (`ax.coastlines()`) in manuscript map figures.
- For **vertical** colorbars (the default for multi-row map figures like E1): use `fraction=0.015`, `pad=0.06`, `aspect=25`.
- For **horizontal** colorbars (used when a single-row ERA5 reference colorbar would cause rotated label overflow — e.g. E2 trend bias maps): use `fraction=0.04`, `pad=0.06`, `aspect=30`. The `pad=0.06` rule applies in both cases. Do not try to switch a figure's colorbar orientation to achieve CLAUDE.md compliance — only fix individual parameter values.
- Row labels: place the variable name once per variable, centered between the train/test row pair (anchor at `y=0` of the first row, `x=-0.10`). Place smaller grey `(train)`/`(test)` labels separately in each row at `x=-0.03`.

### Panel lettering
- Add panel letters `(a)`, `(b)`, … in row-major order, placed top-left inside each axes (`va='top'`, `ha='left'`, `x=0.03`, `y=0.97`), bold, at `LABEL_FS`.
- Skip legend and empty panels when incrementing the letter counter.

### General
- Use `LABEL_FS = 7` consistently for all text in manuscript figures (titles, tick labels, axis labels, legend). Tick labels at `LABEL_FS - 1`.
- Model titles on map figures: use `LABEL_FS + 2` (9pt) so they're readable.
- Use `hspace` generously (≥ 0.9–1.1) when titles span 2–3 lines to prevent row-to-row overprinting.
