"""Pull the annual global-mean series out of the wandb `annual` plotly artifacts.

The inference aggregator logs each variable's annual series as a plotly file, whose traces
are `target` (the reanalysis), `gen` (the ensemble mean) and one `_childN` per initial
condition. That is the only place the series exists for these runs -- they were configured
to log metrics without writing output files -- so this extracts it into a small npz that
make_findings_figures.py reads.

Run:  python evaluations/fetch_annual_series.py [variable]
"""

import json
import sys
from pathlib import Path

import numpy as np
import wandb

VAR = sys.argv[1] if len(sys.argv) > 1 else "TMP2m"
OUT = Path(__file__).parent / "figures" / f"annual_{VAR}.npz"

# ACE2.2 first so the reanalysis reference comes from the 2026 ERA5 build, which five of
# the six models are scored against; ACE2.1's 2024-build target differs by <=0.022 K.
RUNS = [
    ("ACE2.2", "long36-ace22-stage2"),
    ("ACE2.1", "ace-aimip-evaluator-1979-2014-RS3-pressure-level-fine-tuned-separate-decoder-RS0"),
    ("P1 seed 0", "long36-p1-rs0"),
    ("P1 seed 1", "long36-p1-rs1"),
    ("P1 seed 2", "long36-p1-rs2"),
    ("P2", "long36-p2-stage3"),
]

api = wandb.Api()
cache = Path("/tmp/annual_plotly")
out: dict[str, np.ndarray] = {}

for tag, name in RUNS:
    runs = sorted(api.runs("ai2cm/ace", filters={"display_name": name}), key=lambda r: r.created_at)
    if not runs:
        print(f"  {tag}: no run named {name}")
        continue
    run = runs[-1]
    entry = run.summary.get(f"inference/annual/{VAR}")
    if entry is None:
        print(f"  {tag}: no annual/{VAR} artifact")
        continue
    fh = run.file(entry["path"]).download(root=str(cache / tag), replace=True, exist_ok=True)
    traces = {t.get("name"): t for t in json.load(open(fh.name))["data"]}
    years = np.asarray(traces["gen"]["x"], dtype=float)
    out["year"] = years
    out[tag] = np.asarray(traces["gen"]["y"], dtype=float)
    # every run carries its own target; keep the first as the reanalysis reference and
    # check the rest agree, since ACE2.1 is scored against the 2024 ERA5 build
    tgt = np.asarray(traces["target"]["y"], dtype=float)
    if "target" not in out:
        out["target"] = tgt
        out["target_from"] = np.array([tag])
    else:
        d = float(np.max(np.abs(tgt - out["target"])))
        print(f"  {tag}: target differs from {out['target_from'][0]}'s by up to {d:.4f} K")
    print(f"  {tag}: {len(years)} years, {int(years[0])}-{int(years[-1])}")

np.savez(OUT, **out)
print(f"wrote {OUT}")
