# Reproducing the AIMIP-1 manuscript figures

This directory bundles the **minimal pre-processed data** (in `notebooks/cached/`, ~140 MB) needed to
regenerate every figure in the AIMIP-1 manuscript, together with the evaluation code. It is
self-contained: **no raw model output or ERA5 download is required.**

## Setup

```bash
make env       # create the conda environment (aimip-evaluations)
make lab       # launch JupyterLab
```

## Reproducing the figures (default)

Each notebook `notebooks/E1`–`E5` ships with `RESTORE_CACHE = True` / `RESET_CACHE = False` (cell 2) and
is organized into markdown sections. With the bundled cache you do **not** run the whole notebook —
run just:

1. the **setup** cells at the top (imports, config),
2. the **Restore minimal cache** cell, then
3. the cells in the **Manuscript figures** section.

You can **skip** the **Data loading & processing** section and the intermediate diagnostic cells — they
read the full (~1.8 TB) raw dataset. Each notebook's top markdown cell repeats these instructions. Figures
are written to `notebooks/figures/manuscript_figures/`.

## What the cache contains

`notebooks/cached/` holds only the **reduced, plot-ready inputs** each figure consumes — not the full
gridded intermediates. Map figures need a small spatial slice (typically `tas`/`pr`); bar/series figures
need only a tiny scalar table (RMS / global-mean / trend), never a full field. See
`notebooks/cached/MANIFEST.md` for the exact file → figure mapping, sizes and checksums.

## Regenerating the cache from raw data (optional)

To rebuild the cache from the full AIMIP submissions (see `README.md` → Data for the download), set
`RESET_CACHE = True` and `RESTORE_CACHE = False` in cell 2 and run the notebook top to bottom. The
processing cells recompute the reduced products from raw and overwrite `notebooks/cached/`.

## Rebuilding this archive

The code+data archive is assembled by `evaluations/build_repro_archive.py`, which writes
`notebooks/cached/MANIFEST.md`, stages the git-tracked tree plus the minimal `cached/*.nc` files, and
produces a `.tar.gz`:

```bash
python evaluations/build_repro_archive.py --outdir /path/to/output
```

Re-run it after regenerating the cache to rebuild the archive. `FIG_MAP` in that script is the source of
truth for which cache files are shipped and which figure each feeds.
