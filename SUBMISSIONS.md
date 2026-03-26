# AIMIP Phase 1 Submissions

V2: Mar. 26, 2026: Added DLESyM submission; added 'version label' column (Brian Henn)

V1: Dec. 15, 2025: Initial submisssion table (Brian Henn)

## Data Access

Submission data is stored on DKRZ S3 (`s3://ai-mip/` at `https://s3.eu-dkrz-1.dkrz.cloud`) and can be accessed anonymously.

Using Python (`s3fs`):

```python
import s3fs

fs = s3fs.S3FileSystem(
    client_kwargs={'endpoint_url': 'https://s3.eu-dkrz-1.dkrz.cloud'},
    anon=True,
)

# Download a full model submission (replace <OrgName> and <ModelName> as needed)
fs.get('ai-mip/<OrgName>/<ModelName>/', './local_data/<OrgName>/<ModelName>/', recursive=True)
```

Using the AWS CLI:

```bash
# Download a full model submission (replace <OrgName> and <ModelName> as needed)
aws s3 sync s3://ai-mip/<OrgName>/<ModelName>/ ./local_data/<OrgName>/<ModelName>/ \
    --endpoint-url https://s3.eu-dkrz-1.dkrz.cloud --no-sign-request
```

## Submissions

The following submissions have been made to AIMIP.

| organization name | model name | references | code | experiments[^a] | submitted temporal frequency[^b] | submitted horizontal grid | submitted vertical grid | description | version label | DKRZ store monthly filepath example[^c] |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ArchesWeather/INRIA | ArchesWeather | [^1], [^2], [^3] | https://github.com/gcouairon/ArchesWeather | 'aimip' | daily, monthly | 1°x1° | 7 pressure levels | --- | --- | `s3://ai-mip/ArchesWeather/ArchesWeather-V2/aimip/r1i1p1f1/Amon/ta/gn/ta_Amon_ArchesWeather_aimip_r1i1p1f1_gn_197810-202501.nc` |
| ArchesWeather/INRIA | ArchesWeatherGen | [^1], [^2], [^3] | https://github.com/gcouairon/ArchesWeather | 'aimip' | monthly | 1°x1° | 7 pressure levels | --- | --- | `s3://ai-mip/ArchesWeather/ArchesWeatherGen-V2/aimip/r1i1p1f1/Amon/ta/gn/ta_Amon_ArchesWeatherGen_aimip_r1i1p1f1_gn_197810-202501.nc` |
| Ai2 | ACE2.1-ERA5 | [^4] | https://github.com/ai2cm/ace | 'aimip', 'aimip-p2k', 'aimip-p4k' | daily, monthly | 1°x1° | 13 pressure levels ('gr'), regridded from native 8 model layers via ML that are also submitted ('gn') | ACE2.1-ERA5 is similar to ACE2-ERA5 described in [4], except for the following: 1) AIMIP training/evaluation periods, 2) CO<sub>2</sub> is not a forcing feature, 3) near-surface variables ('tas', 'huss', 'vas', 'uas') are no longer prognostic, and 4) layer norm used instead of instance norm in SFNO blocks | `v20251130` | `s3://ai-mip/Ai2/ACE2-1-ERA5/aimip/r1i1p1f1/Amon/ta/gr/v20251130/ta_Amon_ACE2-ERA5_aimip_r1i1p1f1_gr_197810-202412.nc` |
| University of Washington DLESyM/Durran group; NVIDIA | DLESyM | [^8] | https://github.com/AtmosSci-DLESM/DLESyM | 'aimip', 'aimip-p2k', 'aimip-p4k' | daily, monthly | 1°x1° | subset of pressure levels | Trained on 1983-2016 (i.e., included some AIMIP holdout data in training); evaluations begin in October 1983; only a small subset of variables available. | `v20250825` | `s3://ai-mip/DLESyM/DLESyM/aimip/r1i1p1f1/Amon/ta/gn/v20250825/ta_Amon_DLESyM_aimip_r1i1p1f1_gn_19831016-20241216.nc` |
| Google Research | NeuralGCM | [^5], [^6] | https://github.com/neuralgcm/neuralgcm | 'aimip', 'aimip-p2k', 'aimip-p4k' | daily, monthly | 2.8°x2.8° | 7 pressure levels | --- | `v20260304` (monthly); `v20260306` (some daily variables) | `s3://ai-mip/Google/NeuralGCM/aimip/r1i1p1f1/Amon/ta/gn/v20260304/ta_Amon_NeuralGCM_aimip_r1i1p1f1_gn_197810-202412.nc` |
| Google Research | NeuralGCM-HRD | [^5], [^6] | https://github.com/neuralgcm/neuralgcm | 'aimip', 'aimip-p2k', 'aimip-p4k' | daily, monthly | 1°x1° | 7 pressure levels | This is the same model as NeuralGCM, but the outputs were downscaled to a 1-degree grid. Wind and precipitation variables on pressure levels are less reliable in NeuralGCM-HRD. For comparisons involving wind and precipitation variables on pressure levels, we recommend using the standard NeuralGCM model instead. | `v20260304` (monthly); `v20260305`, `v20260306` (daily variables, split by variable) | `s3://ai-mip/Google/NeuralGCM-HRD/aimip/r1i1p1f1/Amon/ta/gn/v20260304/ta_Amon_NeuralGCM-HRD_aimip_r1i1p1f1_gn_197810-202412.nc` |
| NVIDIA | cBottle | [^7] | https://github.com/NVlabs/cBottle | 'aimip', 'aimip-p2k', 'aimip-p4k' | daily, monthly | HEALPix refinement 6 (~1°) | pressure levels | cBottles AIMIP submission includes five ensemble created from different combinations of training checkpoints. The checkpoint and model configuration are mapped onto the "physics_index". Physics index 1-4 are run in correlated noise inference mode, where the random latent used in diffusion model sampling is correlated in time. This is a notable change with respect to the results in Brenowitz, et. al. 2025. Physics indexes: p1) checkpoints: training-state-000512000.checkpoint, training-state-002048000.checkpoint, training-state-009856000.checkpoint p2) checkpoints: training-state-000512000.checkpoint, training-state-002176000.checkpoint, training-state-009984000.checkpoint p3) checkpoints: training-state-000640000.checkpoint, training-state-002048000.checkpoint, training-state-010112000.checkpoint p4) checkpoints: training-state-000640000.checkpoint, training-state-002176000.checkpoint, training-state-009728000.checkpoint p5) Same checkpoints as p4 but latent space is uncorrelated in time, so every sample is fully independent. The specific humidity field 'huss' is computed from surface pressure and 2m dewpoint. | `v20260323` | `s3://ai-mip/NVIDIA/CMIP6/AIMIP/NVIDIA/cBottle-1-3/aimip/r1i1p1f1/Amon/ta/gn/v20260323/ta_Amon_cBottle-1-3_aimip_r1i1p1f1_gn_197810-202412.nc` |
| UMD-PARETO | MD-1p5 | --- | --- | 'aimip', 'aimip-p2k', 'aimip-p4k' | monthly | 1°x1° | 7 pressure levels | --- | `v20251217` | `s3://ai-mip/UMD-PARETO/MD-1p5/aimip/r1i1p1f1/Amon/ta/gr/v20251217/ta_Amon_MD-1p5_aimip_r1i1p1f1_gr_197810-202412.nc` |

[^a]: 'aimip', 'aimip-p2k', and 'aimip-p4k' experiments are the main AIMIP simulation and the +2 K and +4 K SST perturbation experiments, respectively.
[^b]: 'monthly' indicates monthly average output from Oct. 1, 1978 to December 31, 2024; 'daily' indicates daily average output over 1) Oct. 1, 1978 to December 31, 1979 and 2) January 1, 2024 to December 31, 2024.
[^c]: Example path shown for `ta_Amon`, realization 1, using the default 'aimip' experiment. Grid, label, and time period vary by model.
[^1]: https://arxiv.org/html/2405.14527v1
[^2]: https://arxiv.org/abs/2412.12971
[^3]: https://arxiv.org/abs/2509.15942
[^4]: Watt-Meyer, O., Henn, B., McGibbon, J. et al. ACE2: accurately learning subseasonal to decadal atmospheric variability and forced responses. npj Clim Atmos Sci 8, 205 (2025). https://doi.org/10.1038/s41612-025-01090-0
[^5]: Kochkov, D., Yuval, J., Langmore, I. et al. Neural general circulation models for weather and climate. Nature 632, 1060–1066 (2024). https://doi.org/10.1038/s41586-024-07744-y
[^6]: https://arxiv.org/abs/2412.11973
[^7]: https://arxiv.org/abs/2505.06474
[^8]: https://doi.org/10.1029/2025AV001706
