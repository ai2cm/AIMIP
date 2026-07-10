# Reproducing the AIMIP-1 manuscript figures

This directory ships the **minimal pre-processed data** needed to regenerate every figure in the
AIMIP-1 manuscript, in `notebooks/cached/` (~140 MB, 26 files), together with the evaluation code. It is
self-contained: **no raw model output or ERA5 download is required.** These files are committed to the
repository, so a tagged GitHub release — and the Zenodo archive created from it — carries the data
automatically.

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

You can **skip** the **Data loading & processing** section and the **Supplementary diagnostics** cells —
they read the full (~1.8 TB) raw dataset. Each notebook's top markdown cell repeats these instructions.
Figures are written to `notebooks/figures/manuscript_figures/`.

## What the cache contains

`notebooks/cached/` holds only the **reduced, plot-ready inputs** each figure consumes — not the full
gridded intermediates. Map figures need a small spatial slice (typically `tas`/`pr`); bar/series figures
need only a tiny scalar table (RMS / global-mean / trend), never a full field. Mapping of cache file →
figures it produces:

**E1 — time-mean biases**
- `biases_map_1deg.nc` → `bias_1deg_map_tas_pr`, `app_bias_1deg_map_train_tas`, `app_bias_1deg_map_test_tas`
- `biases_map_2p8deg.nc` → `app_bias_2p8deg_map_tas_pr`
- `rmsb_1deg.nc` → `rmsb_1deg_bar_surface_and_plev`, `app_rmsb_tas_bar`, `app_rmsb_1deg_plev_{ta,hus,ua,va}`
- `rmsb_2p8deg.nc` → `app_rmsb_2p8deg_bar_surface_and_plev`

**E2 — trends**
- `regridded_global_annual_means.nc`, `global_annual_mean_era5.nc` → `trend_series_tas_ens_{false,true}`, `trend_bar_surface_and_plev`, `app_trend_1deg_plev_{ta,hus}`
- `regridded_global_annual_means_2p8deg.nc`, `regridded_global_annual_mean_era5_2p8deg.nc` → `app_trend_series_tas_2p8deg`, `app_trend_bar_2p8deg_surface_and_plev`
- `regridded_trend_1deg.nc`, `regridded_trend_era5_1deg.nc` → `trend_map_1deg`
- `regridded_trend_2p8deg.nc`, `regridded_trend_era5_2p8deg.nc` → `app_trend_map_2p8deg`

**E3 — ENSO correlations**
- `enso_coeff_error_map_1deg.nc`, `enso_coeff_era5_map_1deg.nc` → `enso_coeff_map_1deg`
- `enso_coeff_error_map_2p8deg.nc`, `enso_coeff_era5_map_2p8deg.nc` → `app_enso_coeff_map_2p8deg`
- `enso_coeff_rmse_1deg.nc` → `app_enso_coeff_rmse_bar`
- `enso_coeff_rmse_2p8deg.nc` → `app_enso_coeff_rmse_2p8deg_bar`

**E4 — temporal variance**
- `error_map_1deg.nc`, `daily_anomaly_std_era5_map_1deg.nc` → `daily_variability_error_1deg_map_tas_pr`
- `gm_error_1deg.nc`, `gm_error_1deg_normalized.nc` → `daily_variability_relative_error_1deg_bar_surface_and_plev`
- `error_dry_day_map_1deg.nc`, `dry_day_frac_era5_map_1deg.nc` → `app_dry_day_fraction_1deg_map`

**E5 — perturbed-SST response**
- `combined_1deg_perturbed_sst_response_time_means.nc` → `perturbation_response_map_tas_pr`
- `combined_2p8deg_perturbed_sst_response_time_means.nc` → `app_perturbation_response_map_2p8deg_tas_pr`

## Regenerating the cache from raw data (optional)

To rebuild the cache from the full AIMIP submissions (see `README.md` → Data for the download), set
`RESET_CACHE = True` and `RESTORE_CACHE = False` in cell 2 and run the notebook top to bottom. The
processing cells recompute the reduced products from raw and overwrite `notebooks/cached/`. Regeneration
has been verified to reproduce the committed cache (bit-for-bit up to floating-point round-off).
