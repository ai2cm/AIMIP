.PHONY: env test-env fetch-source stage stage-dry manifest check create-repo probe upload verify verify-full publish tag clean

# Shared with evaluations/ (see evaluations/environment.yml).
ENV_NAME  = aimip-evaluations
CONDA_RUN = conda run -n $(ENV_NAME) --no-capture-output
CONFIG    = dataset.yaml

# Values read from $(CONFIG).
cfg       = $(shell $(CONDA_RUN) python scripts/config.py $(CONFIG) $(1))
REPO_ID   = $(call cfg,repo_id)
REPO_TYPE = $(call cfg,repo_type)
STAGING   = $(call cfg,staging_dir)

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

create-repo:
	$(CONDA_RUN) hf repos create $(REPO_ID) --type $(REPO_TYPE) --private --exist-ok

# Small timing probe (ERA5 daily, ~4.5 GB) before committing to the full upload.
probe:
	HF_XET_HIGH_PERFORMANCE=1 $(CONDA_RUN) hf upload $(REPO_ID) $(STAGING)/ERA5/day_1deg ERA5/day_1deg --type $(REPO_TYPE) --commit-message "Probe upload: ERA5/day_1deg"

# Full upload. Resumable: rerun the same target after an interruption and already-committed files are skipped.
upload:
	HF_XET_HIGH_PERFORMANCE=1 $(CONDA_RUN) hf upload $(REPO_ID) $(STAGING) . --type $(REPO_TYPE) --commit-message "$(MSG)"

# Compare the uploaded revision with MANIFEST.sha256 against the sha256 the Hub reports per
# file: seconds, no local re-reading. Requires `make manifest`.
verify:
	$(CONDA_RUN) python scripts/verify_remote.py $(CONFIG)

# Same end-to-end check without a manifest, using the CLI's built-in verification. It re-reads
# and hashes every local file single-threaded: ~3 h for 1.8 TB.
verify-full:
	$(CONDA_RUN) hf cache verify $(REPO_ID) --type $(REPO_TYPE) --local-dir $(STAGING) --fail-on-missing-files --fail-on-extra-files

# Flip visibility to public. Generate the DOI afterwards in the repo Settings page (UI only).
publish:
	$(CONDA_RUN) hf repos settings $(REPO_ID) --type $(REPO_TYPE) --public

tag:
	$(CONDA_RUN) hf repos tag create $(REPO_ID) $(TAG) --type $(REPO_TYPE) --message "$(MSG)"

# Remove the staging tree (hard links only; source_dir is untouched).
clean:
	rm -rf $(STAGING)
