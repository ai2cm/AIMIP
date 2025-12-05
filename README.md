# AIMIP Phase 1 Specification

Chris Bretherton ([christopherb@allenai.org](mailto:christopherb@allenai.org)), Allen Institute for Artificial Intelligence (Ai2)

The latest dated version is publicly posted on the [AIMIP-1 Github site](https://github.com/ai2cm/AIMIP)  
Interested in participating?  Email me to join our AIMIP Google Group.  
   
Based on the 12/2024 [AIMIP proposal](https://docs.google.com/document/d/1oPP_ia4F-vBZJbPJ820JbyAl6B4kHtQT59Sixj9nEEs/edit?usp=sharing) gdoc and valuable feedback from many comments on earlier versions of this doc from around the world (esp. Nikolai Koldunov) and colleagues in Ai2 Climate Modeling (esp. Brian Henn).  Dated versions

This document should get participants started, but will reflect ongoing improvements  
V1: July 16, 2025  
V2: Aug.13, 2025: 

* Link added to 0.25° Ai2-generated ERA5-based monthly SST/sea ice data set for forcing inference simulations created by Ai2  
* Clarify that submission of daily data from inference simulations is optional.

V3: Sept. 25, 2025:  

* New submission schedule: Initial submissions due by Nov. 30, 2025 \- this acknowledges that it is taking time for groups to complete a submission in the desired output format.   
* ERA5 dataset extended to 01/2025 to include 01/01/25 forcings needed for monthly linear interpolation across 12/2024. The link to the Zenodo forcing dataset was updated to point to the extended version.  
* Suggested work-around for small incompatibilities in ERA5 sea-ice forcing data between land mask and sea-ice fraction in 0.25° cells on land-water boundaries.

V4: Dec. 2, 2025:

* Clarify that submissions can choose between outputting q2m or Td2m  
* Move submission deadlines back two weeks to accommodate technical issues and required legal approvals for some groups.  
* Submitted datasets should have CC-BY 4.0 license (the least restrictive choice)  
* Move initial window for analyzing and possibly correcting baseline submissions to 12/15/2025-1/31/2026  
* Update about AIMIP-1 presentations at AGU on 18 Dec. 2025 and at the March 2026 CMIP workshop.

V5: Dec. 5, 2025:

* Provide guidance for the directory structure of AIMIP-1 submissions.
    


**Goals of AIMIP Phase 1 (AIMIP-1)**

1)  To systematically compare time-mean climate, climate trends and climate variability in multidecadal ‘[AMIP](https://www.wcrp-climate.org/modelling-wgcm-mip-catalogue/modelling-wgcm-mips-2/240-modelling-wgcm-catalogue-amip)’ simulations by AI weather/climate models of the global atmosphere and land surface trained on [ERA5](https://www.ecmwf.int/en/forecasts/dataset/ecmwf-reanalysis-v5) and possibly other observational datasets, and forced by historical sea-surface temperature (SST) and sea-ice concentration. 

2) To develop the capability of AI weather/climate models to output results in a common format compliant with the variable names and conventions assumed for climate models participating in the upcoming [Round 7 of the Coupled Model Intercomparison Project (CMIP7)](https://doi.org/10.5194/egusphere-2024-3874), to enable comprehensive evaluation of AI weather/climate models by the broader climate science community.

3)  To enhance the visibility and credibility of AI weather/climate models and learn about their current strengths and weaknesses

AIMIP-1 leverages the existence of several AI weather/climate models that have recently documented capabilities for historical AMIP simulations, e.g. [Neural GCM](https://doi.org/10.1038/s41586-024-07744-y), [ACE2](https://doi.org/10.1038/s41612-025-01090-0), [CAMulator](https://doi.org/10.48550/arXiv.2504.06007), etc.   

This is envisioned as a first step toward AI weather/climate models that can fully participate in CMIP through credible coupled atmosphere-ocean-land-sea ice simulations.  Future phases of AIMIP may evaluate such models once they are more mature.  AIMIP may in future register as a CMIP7 activity, depending on how this first phase progresses.

**What AIMIP-1 is not**

1) *AIMIP-1 is not a beauty contest*.    
   It is intended to document the current state of the art for AI models of the global atmosphere, including strengths, weaknesses and challenges.  AI models for climate are diverse and rapidly evolving.  The skill of tomorrow’s AI models will likely eclipse today’s models before we even analyze the AIMIP-1 results.   
      
2) *AIMIP-1 outputs are not as comprehensive as for physical climate models*  
   Many AI climate models predict only a small subset of the fields and vertical levels that a physical climate model might use.  For instance, many AI climate models don’t predict cloud properties; they account for them through their space-time covariability with other fields that are predicted, like humidity and temperature.  We will evaluate the credibility of AMIP simulations by AI climate models using key CMIP-like metrics of mean climate and atmospheric variability.  
     
   The requested monthly-mean AIMIP-1 outputs are designed to parsimoniously enable this goal.  It would be premature to accommodate all downstream use cases or specialized analyses of CMIP model outputs.  Similarly, a full multidecadal suite of daily (rather than monthly) data would enable additional analysis of weather variability and extreme events, but would be storage-intensive and is not required to test the basic credibility of AMIP simulations.  A single year of daily data suffices to test whether an AI model has credible weather variability.  
     

**Summary of AIMIP-1 protocol**

To make for meaningful comparison, we welcome atmospheric models with some significant AI component trained on ERA5 historical observations from 1979 to 2014\.     
The main intercomparison analysis effort will focus on \`standard’ model simulations from late 1978 – 2024, which include a 3 month spinup period and end with a 10 year test period.  If your standard model can’t produce all of the requested outputs, you can still submit it but we will only include it in analyses based purely on the submitted outputs.

Each group may also (or only) submit custom versions including architectural tweaks, pre-training, or training using additional observations (e.g. IMERG rainfall), other inputs (e.g. CO2), or observational estimates from another reanalysis or a different period, or numerical climate simulations. .  We’ll use initial condition ensembles to assess unforced natural variability.  To explore out-of-sample generalization, we also request a suite of AMIP-like simulations but with SST uniformly increased by 2 K and 4 K.

AIMIP-1 specifies detailed model output requirements to enable model comparison and use of sophisticated evaluation tools developed by the CMIP community for physics-based climate models.  We recognize this may take some effort on the part of participating models, but it adds enormous long-term value to the intercomparison.  Data will be stored by DKRZ for participating modelers and analysts, then later published to the  [Earth System Grid Federation](https://esgf.github.io/) (ESGF) for access by the wider CMIP community.  Models will be expected to provide detailed documentation of their training approach (including hyperparameter tuning and model selection) and open weights to satisfy the scientific reproducibility requirements of peer-reviewed journals.

**What types of AI models are in scope for AIMIP-1?**  
   
AIMIP-1 does not restrict how AI models are built, because AI models may have very different modeling approaches compared to conventional GCMs.   These approaches may include:

1\. Hybrid architectures (e.g. Neural GCM)  
2\. Full model emulators (e.g. ACE)  
3\. Generative models based on conditional sampling of weather states from a target forced climate (e.g. cBottle)

Because we will measure the geographical fidelity of simulated fields, participating models should have a maximum horizontal grid spacing of no more than 500 km.  

**Training and testing data**

To facilitate a clean intercomparison, all standard model training should be done exclusively based on ERA5 data, including surface forcing by SST and sea-ice concentration.  Ideally, if your AI model specifies topography and/or grid-cell based land and ocean fractions as inputs, you should also derive those from ERA5 (with appropriate regridding) for consistency.  

Although ERA5 goes back to 1940, its  atmospheric state estimation is considered much more accurate in the \`satellite era’ (1979 onward).  For this reason, most AI weather models participating in [WeatherBench 2](https://sites.research.google/weatherbench/) were trained on ERA5 data from 1979 onward.  Traditionally, physics-based climate models have also conducted AMIP simulations on the historical period 1979-onward, starting from [the first Atmospheric Model Intercomparison Project](https://doi.org/10.1175/1520-0477\(1999\)080\<0029:AOOTRO\>2.0.CO;2) initiated in 1989, from which the AMIP acronym derives.  

AIMIP-1 models should use the periods 1979-2014 for model training (including hyperparameter selection) and reserve 2015-2024 for testing only (**please don’t game this, since that reduces the value of this intercomparison** \- we won’t be judgmental in discussing intercomparison results, since we recognize this is just a snapshot of current AI model capabilities).  There are no constraints on the choice of input features used for training, as long as all atmospheric state-dependent features are taken from ERA5.

**AMIP simulation details**

*AIMIP-1 monthly forcing dataset*

An AMIP simulation is one element of the CMIP DECK ([Eyring et al. 2016](https://doi.org/10.5194/gmd-9-1937-2016), [Dunne et al. 2024](https://doi.org/10.5194/egusphere-2024-3874)), the basic suite of simulations required by CMIP6 and CMIP7.  Using monthly forcings is attractive because it keeps the needed forcing file compact with minimal degradation of the simulated climate.  

The CMIP [input4mips](https://pcmdi.llnl.gov/mips/input4MIPs/) project that assembles the needed forcing data for the DECK simulations provides [AMIP specifications of the monthly historical SST and sea-ice fraction](https://input4mips-cvs.readthedocs.io/en/latest/dataset-overviews/amip-sst-sea-ice-boundary-forcing/).   However, it is not quite suitable for AIMIP.  First, it doesn’t extend past 2022, while AIMIP inference simulations will cover through 2024 to maximize the possible length of high-quality observational comparison.  Second, the AMIP algorithm for calculating monthly values for SST and sea-ice fraction is problematic.  It involves specifying mid-month values that, when linearly interpolated in time, give the monthly-mean values in the reference dataset.  This inevitably produces overshoots in the mid-month values.  Sea-ice fraction in some grid cells can switch between near 1 and near 0 in successive months, and the CMIP algorithm occasionally results in mid-month values of sea-ice fraction that are below zero and must be thresholded to zero. This results in small biases in annual-mean sea-ice concentration that have a noticeable effect on the annual mean temperature in some grid cells in the seasonal ice zone.

Instead, we at Ai2 have created a compact [1979-2024 monthly AMIP-like SST and sea-ice forcing dataset to use for AIMIP-1 inference runs](https://doi.org/10.5281/zenodo.16782372) that addresses these issues. It is based on daily outputs from ERA5 on its 0.25° lat/lon grid.  These are averaged to forcing values at the beginning of each month using a centered rectangular averaging window between the midpoints of the previous and current months (to enable linear interpolation during Dec. 2024, the dataset extends until 1/2025).  The SST and sea-ice fraction forcings at intermediate times are obtained by linear interpolation.  This method of generating monthly forcings doesn’t produce data overshoots and preserves the annual time-mean of each forcing field, although individual monthly means are not exactly preserved.  We have checked that when used to force inference runs with our emulator, it produces a climate nearly identical to the use of daily forcing data, even in the seasonal sea-ice zones.  Each modeling group should spatially interpolate this monthly forcing to their native grid, e.g. using the conservative regridding option of [xesmf](https://xesmf.readthedocs.io/en/stable/#).

Note that our ERA5-based sea-ice forcing data has small incompatibilities between the land mask and the sea-ice fraction within 0.25° cells on polar coastlines and lake boundaries.  This is native to ERA5, and is even present in the ERA5 data on a reduced Gaussian grid.  The easiest work-around is to limit sea-ice fraction to 1 \- land fraction.  It might be better to fill the resulting ‘lost’ sea-ice into the closest adjacent coastal cells that have sea-ice \+ land fraction \< 1, but the small added benefit is probably not worth the required effort. 

*Don’t explicitly include CO2 as a forcing*

The AMIP protocol for physics-based models also specifies time-varying concentrations of other greenhouse gases and aerosols, but for simplicity, **AIMIP-1 should not include any input specifying time-varying concentrations of CO2 or other radiative forcers**.  Even for physics-based climate models, the AMIP SST specification strongly controls the climate response, such that additionally including CO2 changes during the AMIP period would only have small climate effects, e. g. a fraction of a Kelvin on land surface temperatures.  Our prior experience at Ai2 is that although adding radiative forcing inputs with systematic anthropogenic trends like CO2 to an AI model can improve AMIP inference within the training period, this can also degrade its out-of-sample performance.  Such inputs strongly co-vary with the resulting forced climate change that is already manifest in the SST forcing; this makes their independent effects difficult for the AI to learn.  Appropriate solutions to this issue are being developed, but are not yet mature.  Unlike physics-based models, AI models can learn most effects of anthropogenic radiative forcing trends from the reanalysis training data, even without explicitly including these inputs.  

*Submit an ensemble of five inference simulations*

All groups should perform an ensemble of five inference simulations forced by AMIP SSTs and sea ice concentration, starting 00 UTC 1 Oct. 1978 and run 46 years until 00 UTC 1 Jan 2025\.  Modeling groups can choose their favored method of ensemble creation. For instance, this could be an initial condition (IC) ensemble using five noise perturbations on the natural ERA5 IC, or ICs from five successive days in ERA5, or five different realizations of a stochastic model.  The three initial months are regarded as a spin-up period, after which the simulation should continue 46 additional years until 00 UTC 1 Jan 2025\. 

*Time span for monthly outputs*

For all submitted simulations, please provide monthly-mean output for the entire 46.25 year period. The years 2015-2024 of these simulations will be analyzed as an out-of-sample test, but we will also look at simulated trends and ENSO variability in the full 1979-2024 period.

*Time spans for optional daily outputs*

For these simulations, we also request (but do not require):

* Daily data from 1 Oct. 1978 \- 31 Dec. 1979 to assess AI model spin-up (first three months) and the simulated PDF of daily weather variability in the following 12 months after memory of the initial conditions is lost  
* Daily data from the full year of 2024 as an out-of-sample test.  

For AIMIP-1, we will only assess the sub-monthly variance of selected fields (e.g. T200, T850, Z500) in the models that provide the requested daily outputs, but other analysts may use this data to examine modes of variability such as annular modes, the MJO, etc.

Some models may not produce stable simulations over the entire requested inference period.  That is still useful information for the broader climate modeling community to hear about.  In that case, please report (even if just by email to me) how long your model ran for before blowing up or producing physically implausible results.  We could summarize such results in a table in our initial publication. 

**Optional AMIP+2K and AMIP+4K simulations to test warm-climate generalization**

Participating models are invited to submit an optional pair of 5-ensemble-member sensitivity simulations identical (including initialization) to the standard AMIP simulation, but in which SST is uniformly changed by amounts dSST \= 2 K and 4 K, without change in sea-ice characteristics.  Requested outputs are the same as for the standard simulation.  In these simulations, the spinup may take more than 3 months, but the initial 15 months of daily data may be useful in understanding the spin-up of time-mean biases in these simulations.    

Note that there is no definitive ground truth for these simulations\!  However, the climate changes from a uniform \+2K or \+4K dSST can be estimated from one or more physics-based climate models; Ai2 can provide examples of such simulation results at analysis time.  Since they are out-of-sample tests, large biases or instability are to be expected.  

**Requested outputs**

CMIP compatibility

A central goal of AIMIP-1 is to be as compatible as possible with the upcoming CMIP7 intercomparison, without being excessively cumbersome.  We have had encouraging and useful discussions with scientific leaders of CMIP about this.  This includes:

* Following CMIP recommendations for naming and organizing our data  
* Producing a sufficiently broad set of CMIP-standard \`baseline climate variables’ to enable productive use of CMIP model evaluation software, without overly stretching what our AI-based climate models naturally simulate.  
* Writing a paper about the AIMIP-1 intercomparison for the EGU journal *Geoscientific Model Development* as part of the CMIP7 special issue.  
* Ultimately publishing our data archive on the ESGF, as is standard for CMIP-related projects.

   
To this end, our data will need to be ‘CMOR-ized’ – names and units for all output variables (including time) should be ‘CF-compliant’ with the [Climate and Forecast Conventions](https://cfconventions.org/) and follow strict CMIP naming protocols.  The CMIP6 specification document, filenames, directory structures etc, can be found at [https://doi.org/10.5281/zenodo.12768886](https://doi.org/10.5281/zenodo.12768886).  This will allow us to better leverage CMIP’s large existing diagnostics infrastructure, including a new comprehensive ‘[rapid evaluation framework](https://wcrp-cmip.org/cmip-phases/cmip7/rapid-evaluation-framework/)’ and efficiently interact with the substantial CMIP model evaluation community.  CMIP7 also has a specified format for filename and directory structure that will streamline publishing our data archive on the ESGF.   Numerous CMIP7 (and earlier) resources are being colocated under the [https://zenodo.org/communities/wcrp-cmip umbrella](https://zenodo.org/communities/wcrp-cmip)

The Alfred Wegener Institute (AWI) is developing a Python package for CMORisation (PyMOR). Materials from their recent workshop are available at [https://github.com/esm-tools/pymor\_workshop](https://github.com/esm-tools/pymor_workshop). Christian Lessig of ECMWF is trying this approach out on ArchesWeatherGen.  Shiheng Duan of PCMDI has CMORized outputs from earlier versions of ACE and NeuralGCM; he could also provide advice. There are numerous examples of CMORizing workflows to build on, see the parallel projects for some standalone examples, see the DRCDP project ([here](https://github.com/PCMDI/DRCDP/tree/main/DataPreparationExamples/DEMO)).

Monthly-mean (Oct. 1978- Dec. 2024\)

The requested outputs from each simulation should be written out in single precision as netcdf (one file for each field).  Zarr stores are less preferable, since they are not CMIP-compliant.  We can convert netcdf submissions to zarr later for analysis convenience.  Netcdfs should use the naming convention:

   CFfieldname\_Amon\_MMM\_aimip\[-p2k,-p4k\]\_rXiXpXfX\_gX\_197810-202412.nc for mandatory runs, where:

* MMM is your self-selected model name, e.g. ACE. Model name can contain dashes (e.g. MPI-ESM1-2-HR, but not underscores).  To indicate that a submission is a custom model rather than a standard model,  include ‘-custom’ in the model name.  
* The square bracket means to use ‘aimip’ for baseline submissions, and ‘aimip-p2k’ and ‘aimip-p4k’ for submissions with uniform 2 K and 4 K SST increases  
* r1i1p1f1 \= ensemble member number, e.g. where r: realisation (i.e. ensemble member), i: initialisation method, p: physics, and f: forcing.   
  * If you only submit one version of the model, name the first ensemble member r1i1p1f1, and only increment the realization (r2, r3, r4, r5) for the other initial condition ensemble members   
  * gX has two options: \`gr\`: regridded data reported on the data provider's preferred target grid, and \`gn\`: data reported on a model's native grid (as requested here). 

Amon denotes AMIP monthly output. 

*Horizontal and vertical grid for outputs*

By popular demand (and since CMIP7 recommends it and CMIP data analysis software supports it), **you should output your data on its native grid** (structured or unstructured). CMIP7 provides [instructions on how to document your grid structure in a standardized way](https://wcrp-cmip.org/wp-content/uploads/2024/07/Essential-Model-Documentation-EMD-for-community-review.pdf).  We are hoping that our AIMIP-1 analysis tools can handle this\! 

There is no restriction on how you report vertical levels (e.g. use of constant pressure levels vs. terrain-following levels); we are hoping that CMIP analysis software will be up to the task of interpolating to standard pressure levels, while recognizing that this may cause biases for AI models that only provide output at a few vertical levels.

For AIMIP-1 analysis, we envision analyzing submitted data on a 1°x1°lat/lon grid after vertically interpolating to the following 7 pressure levels (a storage-saving subset of the standard mandatory reporting levels for rawinsonde balloon measurements):

1000 hPa, 850 hPa, 700 hPa, 500 hPa, 250 hPa, 100 hPa, 50 hPa

Other pressure levels \[in Pa\] commonly used for analysis by CMIP (including the ESMVal package used to evaluate the mean climate of CMIP models) include:

1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100, 70, 50, 30, 20, 10, 5, 1   
   
The WeatherBench-2 project used a 13-level subset with less stratosphere levels: 

  1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100, 50 hPa

*3D fields*  
3D fields should be written as arrays with dims (time, pressure, latitude, longitude)  
At each gridpoint & level, report the following fields \[CFfieldname, MKS units\]:

temperature \[ta, K, e.g., CMIP6 monthly mean field description [here](https://github.com/PCMDI/cmip6-cmor-tables/blob/5d08a879bbc79657c367098a2b84279593e63551/Tables/CMIP6_Amon.json#L1133-L1150)\],   
specific humidity \[hus, kg/kg\],   
eastward wind component \[ua, m/s\],   
northward wind component \[va, m/s\]

*Surface fields*  
In addition, the following surface fields with dims (time, latitude, longitude) should be reported, if your model predicts them:

surface pressure \[ps, Pa\] and/or sea-level pressure \[psl, Pa\]  
surface temperature \[ts, K\] (skin temp. over land or sea ice, SST over ocean, whatever your model uses in grid cells with mixed surface types)  
2 m air temperature \[tas, K\],   
2 m dewpoint temperature \[tdas, K\] AND/OR 2 m specific humidity \[huss, kg/kg\]  
10 m eastward wind \[uas, m/s\],   
10 m northward wind \[vas, m/s\],   
Surface precipitation rate \[pr, kg/(m^2 s)\], includes both liquid and frozen \- this should be computed as a time-averaged rate over the month, rather than from a month of daily snapshots, to avoid adding excessive sampling noise.

*Translating between dewpoint temperature and specific humidity*  
ERA5 tabulates 2 m dewpoint temperature instead of specific humidity, but CMIP requests 2 m specific humidity.   Groups may choose which of these two fields they prefer to output, or to output both fields.  
ECMWF suggests the following formulas for calculating huss from dewpoint temperature (thanks to Stephan Hoyer for pointing this out): [https://prod.ecmwf-forum-prod.compute.cci2.ecmwf.int/t/how-to-calculate-hus-at-2m-huss/1254](https://prod.ecmwf-forum-prod.compute.cci2.ecmwf.int/t/how-to-calculate-hus-at-2m-huss/1254)

Lastly, if you can, please report this time-honored atmospheric circulation metric, used in many measures of mid-latitude atmospheric variability:

500 hPa geopotential height \[zg, m\]

For 4 3D fields with 7 reported vertical levels plus 8 2D fields of 1°x1° output, written at single-precision, the required storage for the monthly fields is:

	(4\*7 \+ 8 vars) \* 180 lats \* 360 lons \* 4 bytes \* 12 months \* 46.25 years \= 5 GB

per submitted simulation.  Thus, the monthly data for a standard AIMIP-1 model submission (5 ensemble members for the AMIP, dSST \= \+2K and \+4K cases \= 15 simulations) requires 75 GB. 

Daily outputs for 2.25 years (1 Oct. 1978 \- 31 Dec. 1979 and 1 Jan.-31 Dec. 2024\)

Same as monthly outputs, but use your best estimate of an average (00-24 UTC) daily values.  For example, for ACE we would use the average over 0,6,12, and 18 UTC instantaneous fields for state variables and the average of 0-6, 6-12, 12-18, and 18-24 UTC vertical fluxes of radiation fields, surface turbulent fluxes, and precipitation (which we predict as 6-hour average values).  

Filename convention for daily netcdf data:

CFfieldname\_day\_MMM\_aimip\[-p2k,-p4k\]\_rXiXpXfX\_gX\_19781001[\-](http://-20241231.nc)19791231.nc  
   
This requires an additional storage per single simulation of

	(4\*7 \+ 8 vars) \* 180 lats \* 360 lons \* 4 bytes \* 2.25 years \* 365 days \= 7.7 GB,

i.e. an additional 115 GB of daily output per full model submission of 15 simulations, for 190 GB total.

In a perfect world, we could save daily outputs from the full 46.25 year simulation, but the required storage would get unwieldy unless we dramatically restricted the number of such outputs.    We recognize that this daily data request does not resolve the diurnal cycle, but it does make for a consistent model intercomparison for AI models that may not all predict fields with the same roll-out timestep.   
 

Directory structure

Following CMIP/ESGF [conventions](https://zenodo.org/records/15670624), we propose using the following directory structure when submitting data to the DKRZ store (see below) for each required variable and time frequency file. While this structure is not strictly required, it will aid in keeping the intercomparison organized.

* directory: {institute}/{model\_name}/{experiment}/{ensemble\_member}/{frequency}/{variable}/{grid}/{version}
* filename: {variable}\_{frequency}\_{model\_name}\_{experiment}\_{ensemble\_member}\_{grid}\_{start\_time}-{end\_time}.nc

Where {experiment} is ‘aimip’, ‘aimip-p2k’, or ‘aimip-p4k’, {frequency} is ‘Amon’ or ‘day’, and {version} is a date-based version identifier (e.g., ‘v20251130’). For example, for the Ai2 ACE2-ERA5 model and primary ‘aimip’ experiment, a directory for the daily air temperature file on the native grid would be: ‘Ai2/ACE2-ERA5/aimip/r1i1p1f1/day/ta/gn/v20251130/’, and one of the files in that directory would be ‘ta\_day\_ACE2-ERA5\_aimip\_r1i1p1f1\_gn\_19781001-19791231.nc’.

Further considerations

Other interesting fields (e.g. radiative or surface turbulent fluxes \[W/m^2\], cloud quantities, grid-column precipitable water \[prw, kg/m^2\]) calculated by your model may optionally be included in your output.  They may enable additional evaluation of your model by experts from the climate model diagnostics community.

Weights for your submitted models should also be submitted to allow other groups to replicate your results.

**Who evaluates the AIMIP-1 submissions?**

Ai2 Climate Modeling can help with coordinating this, based on our experience.  Libby Barnes of Boston University, Nikolai Koldunov of AWI, Will Chapman of NCAR, Maria Molina of UMD, and Hannah Christensen of Oxford have also volunteered to help with this evaluation.

**How will they be stored and distributed?**

Nikolai Koldunov has kindly organized for DKRZ to store and distribute submitted results for AIMIP-1 (within reasonable limits, of course), using a cloud-based distribution mechanism called [EERIE](https://easy.gems.dkrz.de/simulations/EERIE/eerie_data-access_online.html). 

Our vision is that the submissions will be stored and free to download for 1-2 years for AIMIP-1 participants, including by any interested analysts from the CMIP community.  The required storage of \~190 GB per standard or custom model is relatively affordable.  Once a core paper on AIMIP-1 has been accepted by a peer-reviewed domain science journal, we also plan to open the archive of AIMIP-1 model output to independent analyses by other researchers.   This will include publishing the archive on the ESGF, a longer term solution widely accessible to the CMIP-savvy community we are trying to impact.  

Before the core AIMIP-1 paper is published, the authors of any paper, arxiv or conference preprint based on AIMIP-1 outputs must offer coauthorship to all the AIMIP-1 contributing modeling groups before that paper/arxiv/preprint is submitted.

Submitted datasets should have a [Creative Commons CC-BY 4.0 license](https://creativecommons.org/share-your-work/cclicenses/) for unlimited public distribution (this allows others to copy, distribute, adapt, and build upon your work, even commercially, as long as they give you credit for the original creation. It is the most open and least restrictive of the Creative Commons licenses, requiring only that the original author is attributed.)

**Evaluation metrics**

At a minimum, examine (for standard models):

E1: global bias and spatial RMSE of train-period and test-period time means (’root mean square bias’ or RMSB) vs. ERA5 reference.  
E2: train-period and test-period linear trends of these fields  
E3: Regressions of a subset of these fields on Nino3.4 index

All of these will be calculated using the submitted monthly-mean outputs.  We recognize that RMSE slightly favors models that under-simulate unforced internal atmospheric variability, but this is not a beauty contest and RMSE is easy to compute.  

From the 1979 daily data, we will compute:

E4: Maps and global means of temporal standard deviation of selected weather variables (e.g. T850 and Z500), calculated using differences of the daily data from the monthly mean data. 

Other analyses using metrics such as CRPS that explicitly reward a correct level of unforced variability are also welcome.  

Evaluation will also be done with the CMIP Rapid Evaluation Framework (REF, [https://climate-ref.readthedocs.io/en/latest/](https://climate-ref.readthedocs.io/en/latest/)). The REF is a set of Python packages for climate model evaluation and benchmarking using [CMOR](https://github.com/PCMDI/CMOR)ized input data. Its calculations are done by external diagnostic providers, which currently include [ESMValTool](https://esmvaltool.org/), [ILAMB](https://www.ilamb.org/), IOMB, and [PMP](https://pcmdi.github.io/pcmdi_metrics/). As the REF provides a generic interface for running diagnostics, both the diagnostic providers and the specific diagnostics are open to be expanded upon through community effort upon release in October 2025\. Using the REF allows for easy and direct comparison to AI and non-AI CMIP7 simulations, with an additional package to be developed for specified AI diagnostics targeting physical consistency.

The ESMValTool Team (Righi et al. 2020; Eyring et al., 2020, https://github.com/ESMValGroup/ESMValTool) with its expertise in evaluating CMIP models for atmospheric variables (Bock et al., 2020\) and general evaluation diagnostics used in IPCC reports (e.g. Eyring et al., 2021\) will help in implementing both general diagnostics lacking in the first release of the REF, as well as in the development of AI-specific diagnostics. Contact persons for this will be Lisa Bock (DLR) and Bettina Gier (University of Bremen).

The PMP Team (Lee et al. 2024, [https://github.com/PCMDI/pcmdi\_metrics](https://github.com/PCMDI/pcmdi_metrics)) has released [demos](https://pcmdi.github.io/pcmdi_metrics/demo-notebooks.html) in Jupyter Notebook format, which can be also useful for AI model evaluation. The contact person for this will be Jiwoo Lee (LLNL, lee1043@llnl.gov).  
   
**Proposed timeline**

16 Jul 2025:	AIMIP-1 protocol finalized and announced

15 Dec. 2025:	Soft deadline for initial submission of mandatory case results (we will start analyzing submitted results at this time)

15 Jan. 2025:	Deadline for initial submission of warmed-SST cases

16 Dec.-1 Feb. 2025:      	Initial screening and evaluation of results, and time window for correcting submissions  (e.g. data format, unintended NaNs, other errors) 

18 Dec. 2025:	Henn et al. talk ‘[GC42A-01AIMIP Phase 1: An intercomparison of AI climate models](https://agu.confex.com/agu/agu25/meetingapp.cgi/Paper/1990353)’ at AGU Fall Mtg, New Orleans 

1 Mar.- 30 Apr. 2026      	Write up results for climate science journal submission and potential ML conference submission. 	        

9-13 Mar. 2026	[CMIP Community Workshop, Kyoto](https://wcrp-cmip.org/event/cmip2026/). Bretherton et al. talk Session 29, ‘'AIMIP Phase 1: A CMIP-friendly AMIP-style intercomparison of AI climate models'’

**Potentially Useful Reference**

Ullrich, P. A., E.A. Barnes, W. D. Collins, K. Dagon, S. Duan, J. Elms, J. Lee, L.R. Leung, D. Lu, M.J. Molina, and T. A. O’Brien, T.A., 2025: Recommendations for comprehensive and independent evaluation of machine learning‐based Earth system models. Journal of Geophysical Research: Machine Learning and Computation, 2, e2024JH000496, [doi: 10.1029/2024JH000496](https://doi.org/10.1029/2024JH000496)
