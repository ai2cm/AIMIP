# AIMIP Phase 1 Submissions

V1: Dec. 15, 2025: Initial submisssion table (Brian Henn)

## Submissions

The following submissions have been made to AIMIP. 

| organization name | model name | references | code | experiments[^a] | submitted temporal frequency[^b] | submitted horizontal grid | submitted vertical grid | description |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ArchesWeather/INRIA | ArchesWeather | [^1], [^2], [^3] | https://github.com/gcouairon/ArchesWeather | 'aimip' | daily, monthly | 1°x1° | 7 pressure levels | --- |
| ArchesWeather/INRIA | ArchesWeatherGen | [^1], [^2], [^3] | https://github.com/gcouairon/ArchesWeather | 'aimip' | monthly | 1°x1° | 7 pressure levels | --- |
| Ai2 | ACE2.1-ERA5 | [^4] | https://github.com/ai2cm/ace | 'aimip', 'aimip-p2k', 'aimip-p4k' | daily, monthly | 1°x1° | 13 pressure levels ('gr'), regridded from native 8 model layers via ML that are also submitted ('gn') | ACE2.1-ERA5 is similar to ACE2-ERA5 described in [4], except for the following: 1) AIMIP training/evaluation periods, 2) CO<sub>2</sub> is not a forcing feature, 3) near-surface variables ('tas', 'huss', 'vas', 'uas') are no longer prognostic, and 4) layer norm used instead of instance norm in SFNO blocks |
| Google Research | NeuralGCM | [^5], [^6] | https://github.com/neuralgcm/neuralgcm | 'aimip', 'aimip-p2k', 'aimip-p4k' | daily, monthly | 2.8°x2.8° | 7 pressure levels | --- |
| Google Research | NeuralGCM-HRD | [^5], [^6] | https://github.com/neuralgcm/neuralgcm | 'aimip', 'aimip-p2k', 'aimip-p4k' | daily, monthly | 1°x1° | 7 pressure levels | This is the same model as NeuralGCM, but the outputs were downscaled to a 1-degree grid. Wind variables on pressure levels are less reliable in NeuralGCM-HRD. For comparisons involving wind variables on pressure levels, we recommend using the standard NeuralGCM model instead. |
| NVIDIA | cBottle | [^7] | https://github.com/NVlabs/cBottle | 'aimip' | daily, monthly | HEALPix refinement 6 (~1°) | pressure levels | cBottles AIMIP submission includes five ensemble created from different combinations of training checkpoints. The checkpoint and model configuration are mapped onto the "physics_index". Physics index 1-4 are run in correlated noise inference mode, where the random latent used in diffusion model sampling is correlated in time. This is a notable change with respect to the results in Brenowitz, et. al. 2025. Physics indexes: p1) checkpoints: training-state-000512000.checkpoint, training-state-002048000.checkpoint, training-state-009856000.checkpoint p2) checkpoints: training-state-000512000.checkpoint, training-state-002176000.checkpoint, training-state-009984000.checkpoint p3) checkpoints: training-state-000640000.checkpoint, training-state-002048000.checkpoint, training-state-010112000.checkpoint p4) checkpoints: training-state-000640000.checkpoint, training-state-002176000.checkpoint, training-state-009728000.checkpoint p5) Same checkpoints as p4 but latent space is uncorrelated in time, so every sample is fully independent. The specific humidity field 'huss' is computed from surface pressure and 2m dewpoint. |
| UMD-PARETO | MD-1p5 | --- | --- | 'aimip', 'aimip-p2k', 'aimip-p4k' | monthly | 1°x1° | 7 pressure levels | --- |

[^a]: 'aimip', 'aimip-p2k', and 'aimip-p4k' experiments are the main AIMIP simulation and the +2 K and +4 K SST perturbation experiments, respectively.
[^b]: 'monthly' indicates monthly average output from Oct. 1, 1978 to December 31, 2024; 'daily' indicates daily average output over 1) Oct. 1, 1978 to December 31, 1979 and 2) January 1, 2024 to December 31, 2024.
[^1]: https://arxiv.org/html/2405.14527v1
[^2]: https://arxiv.org/abs/2412.12971
[^3]: https://arxiv.org/abs/2509.15942
[^4]: Watt-Meyer, O., Henn, B., McGibbon, J. et al. ACE2: accurately learning subseasonal to decadal atmospheric variability and forced responses. npj Clim Atmos Sci 8, 205 (2025). https://doi.org/10.1038/s41612-025-01090-0
[^5]: Kochkov, D., Yuval, J., Langmore, I. et al. Neural general circulation models for weather and climate. Nature 632, 1060–1066 (2024). https://doi.org/10.1038/s41586-024-07744-y
[^6]: https://arxiv.org/abs/2412.11973
[^7]: https://arxiv.org/abs/2505.06474
