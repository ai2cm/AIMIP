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

<!--
TODO (dataset card, written by the maintainer before `make publish`).
Hugging Face requires this file at the repo root. Suggested sections and sources:

## Summary
  What AIMIP Phase 1 is; link to https://github.com/ai2cm/AIMIP and the preprint.

## Contents
  Table of submissions from SUBMISSIONS.md (drop the MPI-M row; ACE2.2-ERA5 is not yet included),
  plus the ERA5 1-degree monthly/daily reference data. Directory layout follows the CMIP6 DRS
  (<Org>/<Model>/<experiment>/<realization>/<table>/<variable>/<grid>/<version>/file.nc).

## Known gaps
  - NeuralGCM-HRD daily v20260306 (hus, ta, ua, va): some realization/period files were removed
    after a corrupted upload and not replaced; the evaluation code fills them with NaN.
  - ArchesWeather-V2 aimip-p4k has four realizations (r3 absent).
  - cBottle-1-3 aimip-p2k / aimip-p4k contain a single member (r1i1p4f1).

## Usage
  hf download allenai/aimip-phase1-submissions --type dataset --local-dir local_data
  then run the notebooks in evaluations/ (or set AIMIP_DATA_ROOT). Files are CF/CMIP6 NetCDF.

## License
  Root LICENSE.txt: all submission files are copyright of their respective institutions and
  licensed CC BY 4.0; per-submission folders may add guidelines (Ai2/LICENSE-DATASET, NVIDIA/data-card.md).
  ERA5 reference data: Copernicus licence, credit ECMWF/C3S.

## Provenance
  Snapshot of the AIMIP archive hosted by DKRZ (s3://ai-mip) as of 2026-03-31, plus the
  DLESyM v20260406 resubmission (April 2026) and the license/card files. Published while the
  DKRZ store is unavailable; remains the citable snapshot if it returns.

## Citation
  DOI (generated on the Hub after publishing) and the AIMIP Phase 1 preprint.
-->
