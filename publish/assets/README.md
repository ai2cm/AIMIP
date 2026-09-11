---
license: cc-by-4.0
pretty_name: AIMIP Phase 1 model submissions
tags:
  - climate
  - atmosphere
  - netcdf
  - cmip6
  - aimip
---

# AIMIP Phase 1 model submissions

## Summary

This dataset contains output from six model submission groups' ~46-year atmospheric simulations produced as contributions to the AI Model Intercomparison Project (AIMIP) Phase 1. AIMIP systematically evaluates AI weather/climate models trained on ERA5 reanalysis by running standardized AMIP-style simulations and comparing their climate statistics against reference observations and conventional models.

There are currently eight model submissions from the six model submission groups. For each submission, there are typically 15 simulations spanning 5 ensemble members (different initial atmospheric conditions) and 3 sea surface temperature (SST) forcing scenarios — historical baseline, +2 K, and +4 K uniform global SST perturbations — covering October 1978 through December 2024. Outputs are CMIP6-compliant NetCDF files at monthly and, for most submissions, daily mean temporal resolution, at approximately 1° global resolution, on each model's own grid (NeuralGCM is the exception, at 2.8°).

For the AIMIP Phase 1 specification that defines the model training and the required simulations that produced the output here, see https://github.com/ai2cm/AIMIP. For the initial evaluations conducted using a snapshot of this dataset, see https://arxiv.org/abs/2605.06944.

## Contents

| Group | Submission | Directory | Experiments | Frequency | Horizontal grid | Vertical grid |
|---|---|---|---|---|---|---|
| Ai2 | ACE2.1-ERA5 | `Ai2/ACE2-1-ERA5` | `aimip`, `aimip-p2k`, `aimip-p4k` | daily, monthly | 1° × 1° | 13 pressure levels (`gr`), regridded from native 8 model layers via ML; native layers also submitted (`gn`) |
| ArchesWeather | ArchesWeather | `ArchesWeather/ArchesWeather-V2` | `aimip`, `aimip-p2k`, `aimip-p4k` | daily, monthly | 1° × 1° | 7 pressure levels |
| ArchesWeather | ArchesWeatherGen | `ArchesWeather/ArchesWeatherGen-V2` | `aimip`, `aimip-p2k`, `aimip-p4k` | daily, monthly | 1° × 1° | 7 pressure levels |
| NVIDIA | cBottle-1.3 | `NVIDIA/CMIP6/AIMIP/NVIDIA/cBottle-1-3` | `aimip`, `aimip-p2k`, `aimip-p4k` | daily, monthly | HEALPix order 6 (~0.9°) | 8 pressure levels |
| University of Washington and NVIDIA | DLESyM | `DLESyM/DLESyM` | `aimip`, `aimip-p2k`, `aimip-p4k` | daily, monthly | HEALPix order 6 (~0.9°) | some surface, 850 hPa and 500 hPa variables |
| University of Maryland (PARETO group) | MD-1.5 v0.9 | `UMD-PARETO/MD-1p5` | `aimip`, `aimip-2k`, `aimip-4k` | monthly | 1.5° × 1.5° native; 1° × 1° submitted (`gr`) | 7 pressure levels |
| Google Research | NeuralGCM | `Google/NeuralGCM` | `aimip`, `aimip-p2k`, `aimip-p4k` | daily, monthly | 2.8° × 2.8° | 32 sigma levels native; 7 pressure levels submitted |
| Google Research | NeuralGCM-HRD | `Google/NeuralGCM-HRD` | `aimip`, `aimip-p2k`, `aimip-p4k` | daily, monthly | 1° × 1° | 32 sigma levels native; 7 pressure levels submitted |

### References

Model and code citations follow Table 1 of the [AIMIP Phase 1 evaluation paper](https://arxiv.org/abs/2605.06944).

| Submission | Model reference | Code |
|---|---|---|
| ACE2.1-ERA5 | Watt-Meyer et al. (2025), [doi:10.1038/s41612-025-01090-0](https://doi.org/10.1038/s41612-025-01090-0) | Henn et al. (2026), [doi:10.5281/zenodo.19831256](https://doi.org/10.5281/zenodo.19831256) |
| ArchesWeather, ArchesWeatherGen | Couairon et al. (2026), [doi:10.1126/sciadv.adx2372](https://doi.org/10.1126/sciadv.adx2372); Singh et al. (2026), [arXiv:2605.29976](https://arxiv.org/abs/2605.29976) | Couairon et al. (2026), [doi:10.5281/zenodo.20784771](https://doi.org/10.5281/zenodo.20784771) |
| cBottle-1.3 | Brenowitz et al. (2025), [arXiv:2505.06474](https://arxiv.org/abs/2505.06474) | Manshausen et al. (2026), [doi:10.5281/zenodo.20832634](https://doi.org/10.5281/zenodo.20832634) |
| DLESyM | Cresswell-Clay et al. (2025), [doi:10.1029/2025AV001706](https://doi.org/10.1029/2025AV001706) | Cresswell-Clay (2026), [doi:10.5281/zenodo.21270137](https://doi.org/10.5281/zenodo.21270137) |
| MD-1.5 v0.9 | Hall and Molina (2026), [arXiv:2604.13481](https://arxiv.org/abs/2604.13481) | Hall and Molina (2026), [doi:10.5281/zenodo.21430292](https://doi.org/10.5281/zenodo.21430292) |
| NeuralGCM, NeuralGCM-HRD | Kochkov et al. (2024), [doi:10.1038/s41586-024-07744-y](https://doi.org/10.1038/s41586-024-07744-y); Yuval et al. (2026), [doi:10.1126/sciadv.adv6891](https://doi.org/10.1126/sciadv.adv6891) | Kochkov et al. (2026), [doi:10.5281/zenodo.21303721](https://doi.org/10.5281/zenodo.21303721) |

Notes on the table:

- **DLESyM and cBottle-1.3 are on HEALPix grids** rather than latitude/longitude. The resolution is comparable to the 1° submissions, but the data must be remapped before gridpoint comparison with them. In the files, DLESyM carries `face`, `height` and `width` dimensions and cBottle-1.3 a single `i` dimension of 49152 cells.
- **DLESyM pressure-level output**, as submitted, is `ta` at 850 hPa and `zg` at 250, 500 and 1000 hPa.
- **MD-1.5 v0.9 uses `aimip-2k` and `aimip-4k`** as experiment IDs, without the `p` the other submissions use. Code that globs across submissions has to allow for both spellings.
- **NeuralGCM-HRD** is the same model as NeuralGCM downscaled to a 1° grid. Its pressure-level wind and precipitation fields are less reliable; use NeuralGCM for comparisons involving those.
- **DLESyM** was trained on 1983–2016 and so saw some of the AIMIP holdout period during training. Only a small subset of variables is available.
- Per-submission documentation, where the group provided it, is published alongside the data (for example `Ai2/DATASET_CARD.md`, `Ai2/LICENSE-DATASET`, `NVIDIA/README.md`, `NVIDIA/data-card.md`).

### Reference data

`ERA5/mon_1deg/` holds monthly-mean ERA5 for 1978–2024 regridded to 1°, one file per variable (`hus`, `pr`, `ps`, `psl`, `ta`, `tas`, `tdas`, `ts`, `ua`, `uas`, `va`, `vas`, `zg`). `ERA5/day_1deg/` holds daily-mean ERA5 for October 1978 – December 1979 at 1°. These were prepared for AIMIP evaluation by Nikolay Koldunov and Bettina Gier.

## Experiment design

AIMIP Phase 1 compares AI weather/climate models through standardized multidecadal AMIP-style simulations. Its goals are to (1) systematically compare time-mean climate, trends, and variability across AI models trained on ERA5; (2) produce CMIP7-compatible outputs so the broader climate science community can evaluate them; and (3) strengthen the credibility of AI climate models through structured intercomparison. See the [AIMIP specification](https://github.com/ai2cm/AIMIP) for the full protocol.

| Parameter | Value |
|---|---|
| Simulation period | Oct 1, 1978 – Dec 31, 2024 |
| Spinup period | Oct–Dec 1978 (3 months, excluded from analysis) |
| Analysis period | Jan 1, 1979 – Dec 31, 2024 |
| Ensemble members | 5 per experiment (typical) |
| SST scenarios | 3 (baseline, +2 K, +4 K) |
| Total simulations | 15 per submission (typical) |

### Forcing

Models are forced with prescribed monthly sea surface temperature and sea-ice concentration derived from ERA5, spatially interpolated by each group to its own native grid. AIMIP supplies a common [1979–2024 monthly AMIP-like SST and sea-ice forcing dataset](https://doi.org/10.5281/zenodo.16782372) built from daily 0.25° ERA5 output; it extends into January 2025 so that linear interpolation through December 2024 is well defined.

| Experiment ID | Forcing |
|---|---|
| `aimip` | Historical observed SST and sea-ice concentration (baseline) |
| `aimip-p2k` (`aimip-2k` for MD-1.5) | Historical SST with a uniform global +2 K perturbation |
| `aimip-p4k` (`aimip-4k` for MD-1.5) | Historical SST with a uniform global +4 K perturbation |

### Ensemble members

Each scenario is run five times, from different atmospheric states on or around October 1, 1978, labelled `r1i1p1f1` through `r5i1p1f1`. cBottle-1.3 is the exception: its five members differ by training-checkpoint combination rather than initial condition, and are labelled `r1i1p1f1` through `r1i1p5f1` (the "physics index"); see `NVIDIA/README.md`.

### Output frequencies

- **`Amon`** (monthly means): the full simulation period, October 1978 – December 2024. ArchesWeather submissions extend one month further, through January 2025.
- **`day`** (daily means): two sub-periods only — October 1978 – December 1979 (spinup assessment) and January – December 2024 (out-of-sample testing). DLESyM instead submitted continuous daily output from 1978 to 1984.

## File organization

Files are NetCDF4, CF-compliant, and follow CMIP6 naming conventions for variables, units, and coordinates. They are laid out in a CMIP6 Data Reference Syntax (DRS) hierarchy below each submission directory:

```
<experiment_id>/<variant_label>/<table_id>/<variable>/<grid_label>/<version>/<filename>.nc
```

| Field | Values |
|---|---|
| `experiment_id` | `aimip`, `aimip-p2k`, `aimip-p4k` (`aimip-2k` / `aimip-4k` for MD-1.5) |
| `variant_label` | `r1i1p1f1` – `r5i1p1f1` (cBottle-1.3: `r1i1p1f1` – `r1i1p5f1`) |
| `table_id` | `Amon` (monthly mean) or `day` (daily mean) |
| `grid_label` | `gn` (model's native grid) or `gr` (regridded, e.g. to standard pressure levels) |
| `version` | e.g. `v20260304`; ArchesWeather submissions have no version directory |

The filename repeats the same fields:

```
<variable>_<table_id>_<source_id>_<experiment_id>_<variant_label>_<grid_label>_<start>-<end>.nc
```

Examples:

```
Ai2/ACE2-1-ERA5/aimip/r1i1p1f1/Amon/ta/gr/v20251130/ta_Amon_ACE2-ERA5_aimip_r1i1p1f1_gr_197810-202412.nc
Google/NeuralGCM/aimip-p4k/r2i1p1f1/day/tas/gn/v20260305/tas_day_NeuralGCM_aimip-p4k_r2i1p1f1_gn_20240101-20241231.nc
ArchesWeather/ArchesWeather-V2/aimip/r1i1p1f1/Amon/pr/gn/pr_Amon_ArchesWeather_aimip_r1i1p1f1_gn_197810-202501.nc
```

Variable coverage differs by submission. All eight provide `ta`, `zg`, and `tas`; most provide `hus`, `ua`, `va`, `uas`, `vas`, `pr`, `ps`, and `ts`. DLESyM provides only `ta`, `zg`, `tas`, and `pr`. cBottle-1.3 additionally provides radiative and column-integrated fields (`rlut`, `rsds`, `rsut`, `prw`, `clivi`). ArchesWeather submissions provide `tos` and `psl`; NeuralGCM provides `tdas`.

## Usage

Download the whole dataset, or a subset, with the Hugging Face CLI:

```bash
# everything (~1.8 TB)
hf download allenai/aimip-phase1-submissions --type dataset --local-dir local_data

# one submission plus the ERA5 reference data
hf download allenai/aimip-phase1-submissions --type dataset --local-dir local_data \
    --include "DLESyM/*" "ERA5/*"
```

The layout matches what the [AIMIP evaluation notebooks](https://github.com/ai2cm/AIMIP/tree/main/evaluations) expect: place it at `local_data/` in a clone of that repository, or point `AIMIP_DATA_ROOT` at it. Individual files open with any NetCDF tool:

```python
import xarray as xr

ds = xr.open_dataset(
    "local_data/Ai2/ACE2-1-ERA5/aimip/r1i1p1f1/Amon/ta/gr/v20251130/"
    "ta_Amon_ACE2-ERA5_aimip_r1i1p1f1_gr_197810-202412.nc"
)
ta = ds["ta"]  # (time, plev, lat, lon); plev in Pa
```

## Known gaps

These are minor relative to the overall evaluation requirements, but worth knowing before computing ensemble statistics.

- **NeuralGCM-HRD**, daily `v20260306` (`hus`, `ta`, `ua`, `va`): some realization/period files were removed after a corrupted upload and were not replaced. Seven of the 1978–79 files are absent, so those variables have three or four members rather than five for that period.
- **ArchesWeather-V2**, `aimip-p4k`: four realizations; `r3i1p1f1` is absent.
- **cBottle-1.3**, `aimip-p2k` and `aimip-p4k`: a single member (`r1i1p4f1`) rather than five.

The AIMIP evaluation code fills missing realizations with NaN and continues, so ensemble means and medians are taken over the members that exist.

## Provenance

Snapshot of the AIMIP archive hosted by DKRZ at `s3://ai-mip`, taken 2026-03-31, plus the DLESyM `v20260406` resubmission from April 2026 and the license and documentation files. It is published here as a citable, immutable revision of the Phase 1 submissions for the evaluation paper.

The MPI-ESM1-2-LR CMIP6 output that accompanies the archive as a formatting template is not included here, and neither is the native-resolution ERA5 collection.

## License

All submission files are copyright of their respective institutions, organisations, or companies and are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); see `LICENSE.txt` at the root. Individual submission folders may add guidelines consistent with CC BY 4.0, for example `Ai2/LICENSE-DATASET` and `NVIDIA/data-card.md`.

The ERA5 reference data is derived from ECMWF ERA5 reanalysis and is subject to the [Copernicus licence](https://apps.ecmwf.int/datasets/licences/copernicus/); credit ECMWF and the Copernicus Climate Change Service.

This dataset consists entirely of weather and climate model output and reanalysis-derived reference data. It contains no private, personal, or otherwise sensitive data.

## Citation

Please cite this dataset by its DOI, together with the AIMIP Phase 1 evaluation paper (https://arxiv.org/abs/2605.06944) and the papers for the individual model submissions you use, listed in the table above.
