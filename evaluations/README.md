# AIMIP Evaluation Notebooks

Jupyter notebooks for evaluating AIMIP model submissions against ERA5 reanalysis data. Notebooks load model output directly from the DKRZ S3 cloud storage — an active internet connection is required.

## Setup

```bash
conda env create -f environment.yml
conda activate aimip-evaluations
jupyter lab
```

## Notebooks

| Notebook | Description |
|----------|-------------|
| `2026-02-06-time-mean-biases.ipynb` | Time-mean biases vs. ERA5 across training (1979–2014) and test (2015–2024) periods |
| `2026-02-13-trends.ipynb` | Decadal trend comparison between models and ERA5 |
| `2026-02-25-enso-correlations.ipynb` | ENSO teleconnection correlations with the Niño3.4 SST index |
| `2026-02-27-perturbed-sst-response.ipynb` | Atmospheric response to +2 K and +4 K SST perturbation experiments |
| `2026-03-12-temporal-variance.ipynb` | Sub-monthly temporal variance in daily model output vs. ERA5 |

## Utility Modules

- `aimip_data_utils.py` — data loading, regridding, and processing functions shared across notebooks
- `enso_index.py` — Niño3.4 ENSO index data and xarray conversion utilities
