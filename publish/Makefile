.PHONY: check-config env test-env fetch-source stage stage-dry manifest check create-repo probe upload verify verify-full publish tag clean

# Shared with evaluations/ (see evaluations/environment.yml).
ENV_NAME  = aimip-evaluations
CONFIG    = dataset.yaml

# `conda` is usually only a shell function from `conda init`, so it is not on PATH
# inside make. Resolve the executable, and let the caller override: make CONDA=/path/to/conda
CONDA    ?= $(shell command -v conda 2>/dev/null || echo $(HOME)/miniconda3/bin/conda)
CONDA_RUN = $(CONDA) run -n $(ENV_NAME) --no-capture-output

# Config values are read by whichever python can import pyyaml: the conda env's if it
# exists, else whatever is on PATH. Resolved this way because putting a conda base
# directory on PATH shadows the system python3, which may be the only one with pyyaml.
# Override with: make CFG_PY=/path/to/python
CONDA_BASE := $(patsubst %/bin/conda,%,$(CONDA))
CFG_PY     ?= $(shell for p in "$(CONDA_BASE)/envs/$(ENV_NAME)/bin/python" python3 python; do \
                  command -v "$$p" >/dev/null 2>&1 && "$$p" -c "import yaml" >/dev/null 2>&1 \
                    && { echo "$$p"; break; }; done)
cfg        = $(shell $(CFG_PY) scripts/config.py $(CONFIG) $(1))
REPO_ID   := $(call cfg,repo_id)
REPO_TYPE := $(call cfg,repo_type)
STAGING   := $(call cfg,staging_dir)

# Refuse to run a Hub command with an unresolved repo id or staging path.
check-config:
	@test -n "$(CFG_PY)" || { \
	  echo "no python on PATH can import pyyaml. Override with: make CFG_PY=/path/to/python"; exit 1; }
	@test -n "$(REPO_ID)" -a -n "$(REPO_TYPE)" -a -n "$(STAGING)" || { \
	  echo "could not read repo_id/repo_type/staging_dir from $(CONFIG) using '$(CFG_PY)'"; exit 1; }
	@test -x "$(CONDA)" || command -v "$(CONDA)" >/dev/null || { \
	  echo "conda not found at '$(CONDA)'. Override with: make CONDA=/path/to/conda"; exit 1; }

# Overridable on the command line, e.g. `make upload MSG="..."`, `make tag TAG=phase1-2026-09`.
MSG ?= AIMIP Phase 1 submissions snapshot
TAG ?= phase1-$(shell date +%Y-%m)

# Create or update the shared conda env (adds huggingface_hub + pyyaml to aimip-evaluations).
env:
	conda env update -n $(ENV_NAME) -f ../evaluations/environment.yml || conda env create -f ../evaluations/environment.yml

test-env:
	$(CONDA_RUN) python -c "import yaml, huggingface_hub, hf_xet; print('huggingface_hub', huggingface_hub.__version__, 'OK')"
	$(CONDA_RUN) hf auth whoami

# Materialize source_dir from the DKRZ archive (only works while the store is reachable).
fetch-source:
	$(CONDA_RUN) python scripts/fetch_source.py $(CONFIG)

# Assemble the publishable tree from source_dir (hard links) + assets/.
stage-dry:
	$(CONDA_RUN) python scripts/stage.py $(CONFIG) --dry-run

stage:
	$(CONDA_RUN) python scripts/stage.py $(CONFIG) --prune

# sha256 of every staged file -> $(STAGING)/MANIFEST.sha256, hashed in parallel (~25 min for
# 1.8 TB). Run any time before `make verify`; also the committed record of a published revision.
manifest:
	$(CONDA_RUN) python scripts/manifest.py $(CONFIG)

# Enforce scope rules and expected totals on the staged tree (fast, no hashing).
check:
	$(CONDA_RUN) python scripts/manifest.py $(CONFIG) --check

create-repo: check-config
	$(CONDA_RUN) hf repos create $(REPO_ID) --type $(REPO_TYPE) --private --exist-ok

# Small timing probe (ERA5 daily, ~4.5 GB) before committing to the full upload.
probe: check-config
	HF_XET_HIGH_PERFORMANCE=1 $(CONDA_RUN) hf upload $(REPO_ID) $(STAGING)/ERA5/day_1deg ERA5/day_1deg --type $(REPO_TYPE) --commit-message "Probe upload: ERA5/day_1deg"

# Full upload. Resumable: rerun the same target after an interruption and already-committed files are skipped.
upload: check-config
	HF_XET_HIGH_PERFORMANCE=1 $(CONDA_RUN) hf upload $(REPO_ID) $(STAGING) . --type $(REPO_TYPE) --commit-message "$(MSG)"

# Compare the uploaded revision with MANIFEST.sha256 against the sha256 the Hub reports per
# file: seconds, no local re-reading. Requires `make manifest`.
verify: check-config
	$(CONDA_RUN) python scripts/verify_remote.py $(CONFIG)

# Same end-to-end check without a manifest, using the CLI's built-in verification. It re-reads
# and hashes every local file single-threaded: ~3 h for 1.8 TB.
verify-full: check-config
	$(CONDA_RUN) hf cache verify $(REPO_ID) --type $(REPO_TYPE) --local-dir $(STAGING) --fail-on-missing-files --fail-on-extra-files

# Flip visibility to public. Generate the DOI afterwards in the repo Settings page (UI only).
publish: check-config
	$(CONDA_RUN) hf repos settings $(REPO_ID) --type $(REPO_TYPE) --public

tag: check-config
	$(CONDA_RUN) hf repos tag create $(REPO_ID) $(TAG) --type $(REPO_TYPE) --message "$(MSG)"

# Remove the staging tree (hard links only; source_dir is untouched).
clean:
	rm -rf $(STAGING)
