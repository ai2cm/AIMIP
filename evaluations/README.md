# AIMIP Evaluation Notebooks

Jupyter notebooks for evaluating AIMIP model submissions against ERA5 reanalysis data. Notebooks read from local data files that must be downloaded in advance (see **Data** below).

## Data

Notebooks require local copies of AIMIP model submissions and ERA5 reference data. These can be downloaded from either of two sources, described under [Downloading data](#downloading-data) below: the DKRZ S3 store, which holds the complete archive, or the Hugging Face dataset, a citable snapshot of the subset these notebooks read.

By default, data is expected at `local_data/` at the repo root. To use a different path, set the `AIMIP_DATA_ROOT` environment variable before launching Jupyter:

```bash
export AIMIP_DATA_ROOT=/path/to/your/data
```

The output directories can also be overridden (they are created automatically on first run if absent):

```bash
export AIMIP_FIGURES_DIR=/path/to/figures   # default: ./figures
export AIMIP_CACHE_DIR=/path/to/cached      # default: ./cached
```

### Downloading data

The same files are available from two places. Both produce the `local_data/` layout the notebooks expect.

| Source | Contents | Use it for |
|---|---|---|
| DKRZ S3, `s3://ai-mip/` | the live archive: every submission, the MPI-ESM1-2-LR formatting template, native-resolution ERA5 and GPCP-SG | the authoritative, current copy |
| Hugging Face, [`allenai/aimip-phase1-submissions`](https://huggingface.co/datasets/allenai/aimip-phase1-submissions) | a fixed snapshot of exactly what the E1–E5 notebooks read, about 1.8 TB | reproducing the published evaluation; a single resumable command |

#### From DKRZ S3

```python
import s3fs

fs = s3fs.S3FileSystem(
    client_kwargs={'endpoint_url': 'https://s3.dkrz.cloud'},
    anon=True,
)

# Download a full model submission (replace <OrgName> and <ModelName> as needed)
fs.get('ai-mip/<OrgName>/<ModelName>/', './local_data/<OrgName>/<ModelName>/', recursive=True)

# Download ERA5 reference data
fs.get('ai-mip/ERA5/', './local_data/ERA5/', recursive=True)
```

Alternatively, using the AWS CLI:

```bash
# Download a full model submission (replace <OrgName> and <ModelName> as needed)
aws s3 sync s3://ai-mip/<OrgName>/<ModelName>/ ./local_data/<OrgName>/<ModelName>/ \
    --endpoint-url https://s3.dkrz.cloud --no-sign-request

# Download ERA5 reference data
aws s3 sync s3://ai-mip/ERA5/ ./local_data/ERA5/ \
    --endpoint-url https://s3.dkrz.cloud --no-sign-request
```

#### From Hugging Face

```bash
pip install "huggingface_hub[hf_xet]"

# Everything the notebooks read (~1.8 TB), straight into local_data/
hf download allenai/aimip-phase1-submissions --type dataset --local-dir local_data

# Or one submission plus the ERA5 reference data
hf download allenai/aimip-phase1-submissions --type dataset --local-dir local_data \
    --include "DLESyM/*" "ERA5/*"

# Or the exact revision evaluated in the paper
hf download allenai/aimip-phase1-submissions --type dataset --local-dir local_data \
    --revision phase1-2026-09
```

Downloads resume if interrupted: rerun the same command and completed files are skipped.

This snapshot is citable as **DOI [10.57967/hf/10490](https://doi.org/10.57967/hf/10490)**. It is the submission data the evaluations use, pinned to the revision behind the published results, plus the 1° ERA5 reference data. It deliberately omits the MPI-ESM1-2-LR formatting template, the native-resolution `ERA5/mon` collection and `GPCP-SG`, none of which the E1–E5 notebooks read; take those from DKRZ if you need them. Its dataset card documents the per-submission grids, variables and known gaps.

### Starting from DKRZ

The Hugging Face snapshot already is what the notebooks read. If you sync from DKRZ instead, five things need attention. Compared file-by-file on 2026-09-18.

- **Some files the evaluation config expects under `v20260304` are published on DKRZ only under `v20260305`.** This affects 78 NeuralGCM and NeuralGCM-HRD files, mostly monthly `ps`, `tas`, `tdas` and `ts` for the `+2K` and `+4K` experiments. Synced as-is they simply will not be found, and the loader substitutes NaN.
- **Three monthly NeuralGCM-HRD files are truncated under `v20260304`**: `aimip` r1 `ua`, `aimip` r2 `tas`, and `aimip-p4k` r3 `pr`. DKRZ publishes the intact copies under `v20260312`; one was checked byte-for-byte against the snapshot and matches. The same pattern affects one daily file under `v20260309`.
- **Thirty NeuralGCM-HRD daily `v20260306` files are truncated and will not open.** These are the originals behind the known gap described in the dataset card, not replacements for it. Every one has a size that is an exact multiple of 1 MiB, which no intact file in the archive does.
- **ERA5 is incomplete on DKRZ**: the `ERA5/day_1deg` NetCDF that E4 reads is absent, as are the 1° monthly `Amon_pr` and `Amon_tdas`. Take ERA5 from the snapshot or from any other ERA5 source.
- **Several trees can be skipped.** Nothing in E1–E5 reads `MPI-M/`, `ERA5/mon/`, `GPCP-SG/` or `catalog/`. `ArchesWeather/ArchesWeatherGen-V2/aimip-era5/` duplicates files already present at their correct paths.

### Expected directory structure

```
local_data/
├── Ai2/
├── ArchesWeather/
├── DLESyM/
├── Google/
├── NVIDIA/
├── UMD-PARETO/
└── ERA5/
```

### ERA5 evaluation data

ERA5 monthly and daily data for use in AIMIP evaluations has also been made available on the DKRZ store by Nikolay Koldunov and Bettina Gier.

## Setup

```bash
make env       # create the conda environment
make test-env  # verify all dependencies are importable
make lab       # launch JupyterLab interactively
```

To execute notebooks non-interactively:

```bash
make E1        # execute a single notebook in-place
make execute   # execute all notebooks
```

## Notebooks

| Notebook | Description |
|----------|-------------|
| `E1-time-mean-biases.ipynb` | Time-mean biases vs. ERA5 across training (1979–2014) and test (2015–2024) periods |
| `E2-trends.ipynb` | Decadal trend comparison between models and ERA5 |
| `E3-enso-correlations.ipynb` | ENSO teleconnection correlations with the Niño3.4 SST index |
| `E4-temporal-variance.ipynb` | Sub-monthly temporal variance in daily model output vs. ERA5 |
| `E5-perturbed-sst-response.ipynb` | Atmospheric response to +2 K and +4 K SST perturbation experiments |

## Utility Modules

- `notebooks/aimip_data_utils.py` — data loading, regridding, and processing functions shared across notebooks
- `notebooks/enso_index.py` — Niño3.4 ENSO index data and xarray conversion utilities

## Data access approaches

The evaluation notebooks above read data from **local files** that you download in advance — see [Data](#data) above. That's not the only way to consume AIMIP data, and it isn't always the right one. There are three complementary patterns, in increasing abstraction order.

### 1. Local download (default for these E1–E5 notebooks)

Pre-download a model submission with `hf download ...`, `s3fs.get(...)` or `aws s3 sync ...`, then point the notebooks at it via `AIMIP_DATA_ROOT`. Best when:

- you re-read the same files many times (the evaluation notebooks do)
- you want offline-capable, reproducible runs (e.g. CI)
- network egress is expensive or slow

Code: see [Data](#data) above.

### 2. Direct S3 with classical `xarray`

Open one NetCDF at a time, straight from S3, no local copy:

```python
import xarray as xr

ds = xr.open_dataset(
    "s3://ai-mip/Ai2/ACE2-1-ERA5/aimip/r1i1p1f1/Amon/tas/gn/v20251130/"
    "tas_Amon_ACE2-1-ERA5_aimip_r1i1p1f1_gn_197810-202412.nc",
    engine="h5netcdf",
    backend_kwargs={"storage_options": {
        "anon": True,
        "client_kwargs": {"endpoint_url": "https://s3.dkrz.cloud"},
    }},
)
```

Best when: you already know the exact file path, you need just one file, or you're doing one-off exploratory work. End-to-end walkthrough: [`examples/working_with_AIMIP_data.ipynb`](../examples/working_with_AIMIP_data.ipynb).

### 3. Cloud access via the intake catalog

A virtual catalog published at `s3://ai-mip/catalog/` exposes every CMIP6 group as a single merged `xarray.Dataset`, with hierarchical browsing and rich metadata. Two leaves per group: a stock-zarr **kerchunk JSON** path and an **icechunk** path (which is the only published path for ~90 of the 239 stores — Ai2 day, all of DLESyM, Google day).

```python
import intake

S3_OPTS = {"anon": True, "client_kwargs": {"endpoint_url": "https://s3.dkrz.cloud"}}
cat = intake.open_catalog("s3://ai-mip/catalog/CMIP6/catalog.yaml", storage_options=S3_OPTS)

# kerchunk JSON leaf (stock zarr; works for 149 of 239 stores)
ds = cat['AIMIP']['NVIDIA']['cBottle-1-3']['aimip']['r1i1p4f1']['Amon']['gn'].to_dask()

# icechunk leaf (works for all 239 stores; required for Ai2 day, DLESyM, Google day)
ds = cat['AIMIP']['Ai2']['ACE2-1-ERA5']['aimip']['r1i1p1f1']['day']['gn_icechunk'].to_dask()
```

Best when: you want to discover what's available, slice by facets (`institution_id`, `experiment_id`, `variant_label`, …), or treat all variables of a group as one Dataset without manual concat. Multi-file groups, dropped-variable provenance, and version dedup are handled in the build. End-to-end walkthrough: [`examples/working_with_AIMIP_data_via_catalog.ipynb`](../examples/working_with_AIMIP_data_via_catalog.ipynb).

### Picking an approach

| Want to … | Best fit |
|---|---|
| Run E1–E5 here, or any workflow that re-reads files | **Local download** (default) |
| Reproduce the published evaluation from a citable, fixed snapshot | Local download from Hugging Face |
| Open one specific file by an exact path | Direct S3 |
| Browse the archive hierarchically; multi-file groups as one Dataset | Catalog (kerchunk JSON) |
| Read an Ai2 day, DLESyM, or Google day store | Catalog (icechunk — only published path for these) |

### Install

For (1) and (2): `pip install xarray s3fs h5netcdf` (already in `environment.yml`). Downloading from Hugging Face additionally needs `huggingface_hub[hf_xet]`, also in `environment.yml`.

For (3) the catalog:

```bash
pip install xarray intake intake-xarray kerchunk fsspec s3fs zarr jinja2 h5netcdf icechunk aimip-intake-icechunk
```

The catalog tooling is open-source ([source](https://github.com/koldunovn/aimip-data); [`aimip-intake-icechunk`](https://pypi.org/project/aimip-intake-icechunk/) on PyPI, MIT-licensed). A timed side-by-side comparison of the three approaches lives in [the catalog repo's `aimip_catalog_vs_classical.ipynb` notebook](https://github.com/koldunovn/aimip-data/blob/main/notebooks/aimip_catalog_vs_classical.ipynb).
