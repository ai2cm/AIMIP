.PHONY: env test-env lab execute E1 E2 E3 E4 E5

ENV_NAME = aimip-evaluations
CONDA_RUN = conda run -n $(ENV_NAME)

env:
	conda env create -f environment.yml

test-env:
	cd notebooks && $(CONDA_RUN) python -c "import xarray, numpy, dask, cartopy, matplotlib, xesmf, healpy, netCDF4, s3fs, fsspec; from aimip_data_utils import AIMIP_EXPERIMENT_SUBMISSIONS; from enso_index import NINO34_INDEX; print('All imports OK')"

lab:
	cd notebooks && $(CONDA_RUN) jupyter lab

execute: E1 E2 E3 E4 E5

E1:
	$(CONDA_RUN) jupyter nbconvert --to notebook --execute --inplace notebooks/E1-time-mean-biases.ipynb

E2:
	$(CONDA_RUN) jupyter nbconvert --to notebook --execute --inplace notebooks/E2-trends.ipynb

E3:
	$(CONDA_RUN) jupyter nbconvert --to notebook --execute --inplace notebooks/E3-enso-correlations.ipynb

E4:
	$(CONDA_RUN) jupyter nbconvert --to notebook --execute --inplace notebooks/E4-temporal-variance.ipynb

E5:
	$(CONDA_RUN) jupyter nbconvert --to notebook --execute --inplace notebooks/E5-perturbed-sst-response.ipynb
