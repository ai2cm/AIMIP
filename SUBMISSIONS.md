# AIMIP Phase 1 Submissions

V1: Dec. 15, 2025: Initial submisssion table (Brian Henn)

## Submissions

The following submissions have been made to AIMIP. 

| organization name | model name | references | code | experiments[^a] | submitted temporal frequency[^b] | submitted horizontal grid | submitted vertical grid | description |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ArchesWeather/INRIA | ArchesWeather | [^1],[^2],[^3] | https://github.com/gcouairon/ArchesWeather | 'aimip' | daily, monthly | 1°x1° | 7 pressure levels | --- |
| ArchesWeather/INRIA | ArchesWeatherGen | [^1],[^2],[^3] | https://github.com/gcouairon/ArchesWeather | 'aimip' | monthly | 1°x1° | 7 pressure levels | --- |
| Ai2 | ACE2.1-ERA5 | [^4] | https://github.com/ai2cm/ace | 'aimip', 'aimip-p2k', 'aimip-p4k' | daily, monthly | 1°x1° | 13 pressure levels ('gr'), regridded from native 8 model layers via ML that are also submitted ('gn') | ACE2.1-ERA5 is similar to ACE2-ERA5 described in [4], except for the following: 1) AIMIP training/evaluation periods, 2) CO<sub>2</sub> is not a forcing feature, 3) near-surface variables ('tas', 'huss', 'vas', 'uas') are no longer prognostic, and 4) layer norm used instead of instance norm in SFNO blocks |
| Google Research | NeuralGCM | [^5],[^6] | https://github.com/neuralgcm/neuralgcm | 'aimip', 'aimip-p2k', 'aimip-p4k' | daily, monthly | 2.8°x2.8° | 7 pressure levels | --- |
| Google Research | NeuralGCM-HRD | [^5],[^6] | https://github.com/neuralgcm/neuralgcm | 'aimip', 'aimip-p2k', 'aimip-p4k' | daily, monthly | 1°x1° | 7 pressure levels | NeuralGCM with high resolution decoder produces 1° resolution output |
| NVIDIA | cBottle | [^7] | https://github.com/NVlabs/cBottle | 'aimip' | daily, monthly | 0.25°x0.25° | pressure levels | --- |
| UMD-PARETO | MD-1p5 | --- | https://github.com/kjhall01/monthly-diffusion | 'aimip', 'aimip-p2k', 'aimip-p4k' | monthly | 1°x1° | 7 pressure levels | --- |

[^a]: 'aimip', 'aimip-p2k', and 'aimip-p4k' experiments are the main AIMIP simulation and the +2 K and +4 K SST perturbation experiments, respectively.

[^b]: 'monthly' indicates monthly average output from Oct. 1, 1978 to December 31, 2024; 'daily' indicates daily average output over 1) Oct. 1, 1978 to December 31, 1979 and 2) January 1, 2024 to December 31, 2024.

## References:

[^1] https://arxiv.org/html/2405.14527v1

[^2] https://arxiv.org/abs/2412.12971

[^3] https://arxiv.org/abs/2509.15942

[^4] Watt-Meyer, O., Henn, B., McGibbon, J. et al. ACE2: accurately learning subseasonal to decadal atmospheric variability and forced responses. npj Clim Atmos Sci 8, 205 (2025). https://doi.org/10.1038/s41612-025-01090-0

[^5] Kochkov, D., Yuval, J., Langmore, I. et al. Neural general circulation models for weather and climate. Nature 632, 1060–1066 (2024). https://doi.org/10.1038/s41586-024-07744-y

[^6] https://arxiv.org/abs/2412.11973

[^7] https://arxiv.org/abs/2505.06474
