# Publishing the AIMIP Phase 1 dataset to Hugging Face

This directory is a rerunnable workflow that assembles the AIMIP Phase 1 model submissions and
ERA5 reference data into a versioned Hugging Face dataset repository,
[`allenai/aimip-phase1-submissions`](https://huggingface.co/datasets/allenai/aimip-phase1-submissions).

The AIMIP archive is hosted by DKRZ at `s3://ai-mip` (see the [Data section of the evaluation
README](../evaluations/README.md#data)). The Hugging Face dataset is a snapshot of that archive,
published to give the manuscript a DOI-backed, immutable revision to cite and to provide a second
access route. The two coexist: DKRZ is the live archive, Hugging Face the citable snapshot.

The dataset keeps the `local_data/` layout the evaluation notebooks expect, so

```bash
hf download allenai/aimip-phase1-submissions --type dataset --local-dir local_data
```

at the repo root is enough to run `evaluations/notebooks/E1`–`E5` (or set `AIMIP_DATA_ROOT`).

## What is included

Scope is declared in [`dataset.yaml`](dataset.yaml) and is **evaluation-only**: everything the
E1–E5 notebooks on `main` read.

| Included | Not included |
|---|---|
| Ai2 ACE2.1-ERA5 (+ its dataset card and license) | MPI-M MPI-ESM1-2-LR (CMIP6 template, CC BY-SA) |
| ArchesWeather-V2, ArchesWeatherGen-V2 | native-resolution `ERA5/mon` (used only by an example notebook) |
| DLESyM (both submitted versions) | `GPCP-SG` (not read by the notebooks) |
| Google NeuralGCM, NeuralGCM-HRD | Jupyter checkpoint directories, truncated upload leftovers |
| NVIDIA cBottle-1-3 (+ its README, data card, config) | placeholder "area for uploads" READMEs |
| UMD-PARETO MD-1p5 | |
| ERA5 1° monthly and daily reference data | |
| root `LICENSE.txt` and `README.md` (dataset card) | |

About 4,900 files and 1.78 TB. Per-group documentation is published exactly as the groups
submitted it; nothing is generated on their behalf. Small files that override or add to the
source tree live in [`assets/`](assets/) (root dataset card, root license, Ai2 license notice).

## Prerequisites

- The shared conda environment: `make env` (creates or updates `aimip-evaluations` from
  `../evaluations/environment.yml`, which includes `huggingface_hub[hf_xet]` and `pyyaml`).
- A Hugging Face account with write access to the `allenai` organization: `hf auth login`, then `make test-env`.
- A source tree in the `local_data` layout. `make fetch-source` syncs the in-scope prefixes from
  the DKRZ archive with `aws s3 sync` (requires the AWS CLI and access to the store); otherwise
  point `source_dir` in `dataset.yaml` at an existing mirror.
- `staging_dir` on the same filesystem as `source_dir` (the staging tree is hard links, so it
  costs no extra disk).

## Running it

```bash
make env            # once
make test-env       # imports + `hf auth whoami`
make fetch-source   # optional: materialize source_dir from DKRZ
make stage-dry      # print the plan: files and GB per submission
make stage          # hard-link source files + copy assets into staging_dir
make check          # scope rules and expected totals (seconds); must print CHECK OK
make manifest       # sha256 of every staged file, 8 workers (~25 min); needed by `make verify`
make create-repo    # private dataset repo
make probe          # 4.5 GB timing upload (ERA5/day_1deg); note the MB/s before continuing
make upload         # full upload; resumable, rerun the same target after an interruption
make verify         # uploaded revision vs. MANIFEST.sha256 (seconds)
make publish        # flip to public
make tag TAG=phase1-YYYY-MM
```

Then generate the DOI in the dataset's **Settings → DOI** page (UI only), and commit
`staging_dir/MANIFEST.sha256` here as the record of what that revision contains.

Run `make manifest` and `make upload` under `nohup` or `tmux`. `make manifest` does not block
anything else: it only reads the staging tree, so it can run before or during the upload, though
running it during the upload makes both contend for disk.

### Why the manifest

The Hub reports a sha256 for every Xet-tracked file, so `make verify` compares the manifest with
that metadata and finishes in seconds. Without a manifest, `make verify-full` does the same
end-to-end check with the CLI's built-in `hf cache verify`, but that re-reads every local file and
hashes single-threaded at ~180 MB/s: roughly **3 hours** for this tree, against ~25 minutes for a
parallel `make manifest`. Hashing up front is the cheaper order.

## Changing the scope

Edit `dataset.yaml` (`include`, `exclude_globs`, `expected`), then rerun from `make stage`
(`stage` prunes files that dropped out of scope) through `make verify`. Each `make upload` is a new
commit on the dataset repo; generate a new DOI for revisions that should be citable on their own.

## Expectations

| Step | Rough cost |
|---|---|
| `make upload` | 2–5 h for 1.78 TB from a cloud VM; measure with `make probe` first |
| `make manifest` (optional) | 30–40 min at ~1 GB/s local disk read |
| cloud egress | on the order of $150–210 for 1.78 TB leaving GCP |

Hugging Face repository limits (checked September 2026): <100k files per repo, ≤10k entries per
folder, files <200 GB. This dataset is well inside all three (≤26 files per folder, largest file 5.4 GB).
