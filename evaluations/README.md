# AIMIP Evaluation Notebooks

Jupyter notebooks for evaluating AIMIP model submissions against ERA5 reanalysis data. Notebooks read from local data files that must be downloaded in advance (see **Data** below).

## Data

Notebooks require local copies of AIMIP model submissions and ERA5 reference data downloaded from DKRZ S3 (`s3://ai-mip/` at `https://s3.eu-dkrz-1.dkrz.cloud`).

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

```python
import s3fs

fs = s3fs.S3FileSystem(
    client_kwargs={'endpoint_url': 'https://s3.eu-dkrz-1.dkrz.cloud'},
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
    --endpoint-url https://s3.eu-dkrz-1.dkrz.cloud --no-sign-request

# Download ERA5 reference data
aws s3 sync s3://ai-mip/ERA5/ ./local_data/ERA5/ \
    --endpoint-url https://s3.eu-dkrz-1.dkrz.cloud --no-sign-request
```

### Expected directory structure

```
local_data/
├── Ai2/
├── ArchesWeather/
├── Google/
├── NVIDIA/
├── UMD-PARETO/
└── ERA5/
```

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
