import xarray as xr
import numpy as np
import xesmf
import os
import dataclasses
from typing import Literal

DATA_ROOT = '../local_data'
N_REALIZATIONS = 5
GRAVITY = 9.80665 # for geopotential height conversion, standard value
EVALUATION_PRESSURE_LEVELS = [
    100000.,
    85000.,
    70000.,
    50000.,
    25000.,
    10000.,
    5000.,
]

FILE_TEMPLATES = {
    'ACE2-1-ERA5': 
    'r{i_r}i1p1f1/{table}/{varname}/{grid}/{label}/{varname}_{table}_ACE2-ERA5_{experiment_name}_r{i_r}i1p1f1_{grid}_197810-202412.nc',
    'ArchesWeather-V2':
    'r{i_r}i1p1f1/{table}/{varname}/{grid}/{varname}_{table}_ArchesWeather_{experiment_name}_r{i_r}i1p1f1_{grid}_197810-202501.nc',
    'ArchesWeatherGen-V2':
    'r{i_r}i1p1f1/{table}/{varname}/{grid}/{varname}_{table}_ArchesWeatherGen_{experiment_name}_r{i_r}i1p1f1_{grid}_197810-202501.nc',
    'NeuralGCM':
    'r{i_r}i1p1f1/{table}/{varname}/{grid}/{label}/{varname}_{table}_NeuralGCM_{experiment_name}_r{i_r}i1p1f1_{grid}_197810-202412.nc',
    'NeuralGCM-HRD':
    'r{i_r}i1p1f1/{table}/{varname}/{grid}/{label}/{varname}_{table}_NeuralGCM-HRD_{experiment_name}_r{i_r}i1p1f1_{grid}_197810-202412.nc',
    'cBottle':
    'r1i1p{i_r}f1/{table}/{varname}/{grid}/{label}/{varname}_{table}_cBottle-1-3_{experiment_name}_r1i1p{i_r}f1_{grid}_197810-202412.nc',
    'MD-1p5':
    'r{i_r}i1p1f1/{table}/{varname}/{grid}/{label}/{varname}_{table}_MD-1p5_{experiment_name}_r{i_r}i1p1f1_{grid}_197810-202412.nc',
    'ERA5_monthly_1deg':
    'mon_1deg/native6_ERA5_an_v1_Amon_{varname}_1978-2024.nc',
}

@dataclasses.dataclass
class EvaluationVariable:
    standard_name: str
    short_name: str
    long_name: str
    units: str 
    standard_pressure_level_indexer: dict[str, list[float]] | None=None
    interpolate_to_pressure_levels: bool=True

    def __post_init__(self):
        if self.standard_pressure_level_indexer is not None and len(self.standard_pressure_level_indexer) > 1:
            raise ValueError("self.standard_pressure_level_indexer can only contain one indexer.")

    def validate_metadata(self, ds: xr.Dataset) -> xr.Dataset:
        assert self.short_name in ds.data_vars, "dataset contains variable"
        if "units" not in ds[self.short_name].attrs:
            print(f"Missing units attribute for {self.standard_name}, providing from defaults.")
            ds[self.short_name].attrs["units"] = self.units
        if "long_name" not in ds[self.short_name].attrs:
            print(f"Missing long_name attribute for {self.standard_name}, providing from defaults.")
            ds[self.short_name].attrs["long_name"] = self.long_name
        return ds

    def to_standard_pressure_levels(self, ds: xr.Dataset) -> xr.Dataset:
        """If necessary, select and interpolate to standard evaluation levels."""
        if self.standard_pressure_level_indexer is not None:
            pressure_dim_name = list(self.standard_pressure_level_indexer.keys())[0]
            if pressure_dim_name in ds.coords:
                standard_pressure_levels = np.round(self.standard_pressure_level_indexer[pressure_dim_name], 2)
                ds[pressure_dim_name] = np.round(ds[pressure_dim_name], 2)
                if (
                    min(standard_pressure_levels) < ds[pressure_dim_name].min().item()
                    or 
                    max(standard_pressure_levels) > ds[pressure_dim_name].max().item()
                ):
                    raise ValueError("Cannot extrapolate to standard pressure levels.")
                else:
                    if self.interpolate_to_pressure_levels:
                        ds_out = ds.interp({pressure_dim_name: standard_pressure_levels}, method='linear')
                    else:
                        ds_out = ds.sel({pressure_dim_name: standard_pressure_levels}, method='nearest')
                    if ds_out.sizes[pressure_dim_name] == 1:
                        ds_out = ds_out.squeeze().drop_vars(pressure_dim_name)
                    return ds_out
            else:
                print(f'Pressure levels specified but no pressure dimension for {self.standard_name}')
        return ds
 
@dataclasses.dataclass
class ExperimentSubmission:
    submission_dir: str
    file_template: str
    experiment_name: str | None
    label: str | None
    grid: Literal['gr', 'gn']='gn'
    grid_mapping: dict[str, str] | None=None
    renames: dict[str, str] | None=None
    fix_zg: bool = False
    data_root: str=DATA_ROOT

    def __post_init__(self):
        if self.label is None:
            self.label = ''
        if self.experiment_name is None:
            self.experiment_name = ''
        if self.renames is None:
            self.renames = {}
        if self.grid_mapping is None:
            self.grid_mapping = {}
        
    @property
    def name(self) -> str:
        return self.submission_dir

    @property
    def reverse_rename(self) -> dict:
        return {v: k for k, v in self.renames.items()}

    def get_grid_for_variable(self, varname: str) -> str:
        if varname in self.grid_mapping:
            return self.grid_mapping[varname]
        else:
            return self.grid

    def get_variable_path(
        self,
        variable: EvaluationVariable,
        i_r: int,
        table: str,
    ) -> str:
        if variable.short_name in self.renames:
            variable_short_name = self.renames[variable.short_name]
        else:
            variable_short_name = variable.short_name
        file_format = self.file_template.format(
            i_r=i_r,
            table=table,
            varname=variable_short_name,
            grid=self.get_grid_for_variable(variable.short_name),
            label=self.label,
            experiment_name=self.experiment_name,
        )
        return os.path.join(
            self.data_root,
            self.submission_dir,
            self.experiment_name,
            file_format
        )

    def rename_variable(self, ds: xr.Dataset) -> xr.Dataset:
        """Rename if non CMIP-standard names used."""
        for data_var in ds.data_vars:
            if data_var in self.renames.values():
                ds = ds.rename({data_var: self.reverse_rename[data_var]})
        return ds

    def apply_zg_fix(self, ds: xr.Dataset) -> xr.Dataset:
        """Geopotential height is specified but many submitted geopotential instead. """
        if self.fix_zg and 'zg' in ds.data_vars:
            ds['zg'] /= GRAVITY
        return ds

AIMIP_EXPERIMENT_SUBMISSIONS = [
    ExperimentSubmission(
        submission_dir='Ai2/ACE2-1-ERA5',
        experiment_name='aimip',
        file_template=FILE_TEMPLATES['ACE2-1-ERA5'],
        grid='gr',
        grid_mapping={
            'huss': 'gn',
            'pr': 'gn',
            'ps': 'gn',
            'tas': 'gn',
            'ts': 'gn',
            'uas': 'gn',
            'vas': 'gn',   
        },
        label='v20251130'
    ),
    ExperimentSubmission(
        submission_dir='ArchesWeather/ArchesWeather-V2',
        experiment_name='aimip',
        file_template=FILE_TEMPLATES['ArchesWeather-V2'],
        label=None,
        renames={'ts': 'tos'},
        fix_zg=True,
    ),
    ExperimentSubmission(
        submission_dir='ArchesWeather/ArchesWeatherGen-V2',
        experiment_name='aimip',
        file_template=FILE_TEMPLATES['ArchesWeatherGen-V2'],
        label=None,
        renames={'ts': 'tos'},
        fix_zg=True,
    ),
    ExperimentSubmission(
        submission_dir='Google/NeuralGCM',
        experiment_name='aimip',
        file_template=FILE_TEMPLATES['NeuralGCM'],
        label='v20251203',
        fix_zg=True,
    ),
    ExperimentSubmission(
        submission_dir='Google/NeuralGCM-HRD',
        experiment_name='aimip',
        file_template=FILE_TEMPLATES['NeuralGCM-HRD'],
        label='v20251203',
        fix_zg=True,
    ),
    ExperimentSubmission(
        submission_dir='NVIDIA/CMIP6/AIMIP/NVIDIA/cBottle-1-3',
        experiment_name='aimip',
        file_template=FILE_TEMPLATES['cBottle'],
        label='v20260120',
        fix_zg=True,
    ),
    ExperimentSubmission(
        submission_dir='UMD-PARETO/MD-1p5',
        experiment_name='aimip',
        grid='gr',
        file_template=FILE_TEMPLATES['MD-1p5'],
        label='v20251217',
        fix_zg=True,
    ),
]

ERA5_1DEG = ExperimentSubmission(
    submission_dir='ERA5',
    file_template=FILE_TEMPLATES['ERA5_monthly_1deg'],
    experiment_name=None,
    label=None,
)

EVALUATION_VARIABLES = [
    EvaluationVariable(
        standard_name='specific_humidity',
        long_name='specific humidity',
        short_name='hus',
        units='-',
        standard_pressure_level_indexer={'plev': EVALUATION_PRESSURE_LEVELS},
    ),
    EvaluationVariable(
        standard_name='surface_specific_humidity',
        long_name='specific humidity at 2 meters',
        short_name='huss',
        units='-'
    ),
    EvaluationVariable(
        standard_name='dew_point_temperature',
        long_name='dew point temperature at 2 meters',
        short_name='tdas',
        units='K'
    ),
    EvaluationVariable(
        standard_name='precipitation_flux',
        long_name='precipitation_flux at the surface',
        short_name='pr',
        units='kg / s / m **2'
    ),
    EvaluationVariable(
        standard_name='surface_air_pressure',
        long_name='air pressure at the surface',
        short_name='ps',
        units='Pa'
    ),
    EvaluationVariable(
        standard_name='air_pressure_at_sea_level',
        long_name='air pressure at mean sea level',
        short_name='psl',
        units='Pa'
    ),
    EvaluationVariable(
        standard_name='air_temperature',
        long_name='air temperature',
        short_name='ta',
        units='K',
        standard_pressure_level_indexer={'plev': EVALUATION_PRESSURE_LEVELS},
    ),
    EvaluationVariable(
        standard_name='air_temperature',
        long_name='air temperature at 2 meters',
        short_name='tas',
        units='K',
    ),
    EvaluationVariable(
        standard_name='surface_temperature',
        long_name='surface temperature',
        short_name='ts',
        units='K',
    ),
    EvaluationVariable(
        standard_name='eastward_wind',
        long_name='eastward wind',
        short_name='ua',
        units='m s-1',
        standard_pressure_level_indexer={'plev': EVALUATION_PRESSURE_LEVELS},
    ),
    EvaluationVariable(
        standard_name='eastward_wind',
        long_name='eastward wind at 10 meters',
        short_name='uas',
        units='m s-1',
    ),
    EvaluationVariable(
        standard_name='northward_wind',
        long_name='northward wind',
        short_name='va',
        units='m s-1',
        standard_pressure_level_indexer={'plev': EVALUATION_PRESSURE_LEVELS},
    ),
    EvaluationVariable(
        standard_name='northward_wind',
        long_name='northward wind at 10 meters',
        short_name='vas',
        units='m s-1',
    ),
    EvaluationVariable(
        standard_name='geopotential_height',
        long_name='geopotential height',
        short_name='zg',
        units='m',
        standard_pressure_level_indexer={'plev': [5e4]}, # 500 hPa height only
        interpolate_to_pressure_levels=False
    ),
]

def open_variable_from_path(
    path: str,
    evaluation_variable: EvaluationVariable,
    experiment_submission: ExperimentSubmission
) -> tuple[xr.Dataset, bool]:
    try:
        variable_dataset = xr.open_dataset(path, chunks={})
    except FileNotFoundError:
        print(f"Not found: {path}")
        variable_dataset = xr.Dataset()
        missing = True
    else:
        print(path)
        missing = False
        variable_dataset = (
            variable_dataset
            .pipe(experiment_submission.rename_variable)
            .pipe(experiment_submission.apply_zg_fix)
            .pipe(evaluation_variable.validate_metadata)
            .pipe(evaluation_variable.to_standard_pressure_levels)
        )
    # singleton height coordinate for surface variables causes xarray merge conflicts
    variable_dataset = variable_dataset.drop_vars("height", errors="ignore") 
    return variable_dataset, missing

def open_aimip_data(
    experiment_submissions: list[ExperimentSubmission],
    evaluation_variables: list[EvaluationVariable],
    table: Literal['Amon', 'day'],
    n_realizations: int=N_REALIZATIONS,
) -> tuple[dict[str, xr.Dataset], dict[list[str]]]:
    experiment_submission_datasets = {}
    missing_files = {}
    for experiment_submission in experiment_submissions:
        submission_missing_files = []
        print(experiment_submission.name)
        evaluation_variable_datasets = []
        for evaluation_variable in evaluation_variables:
            print(evaluation_variable.standard_name)
            realization_datasets = []
            for i_r in range(1, n_realizations + 1):
                variable_path = experiment_submission.get_variable_path(evaluation_variable, i_r, table)
                realization_dataset, missing = open_variable_from_path(variable_path, evaluation_variable, experiment_submission)
                realization_datasets.append(realization_dataset.expand_dims({'realization': [i_r]}))
                if missing:
                    submission_missing_files.append(variable_path)
            evaluation_variable_dataset = xr.concat(realization_datasets, dim='realization', compat='no_conflicts', join='inner')
            evaluation_variable_datasets.append(evaluation_variable_dataset)
        experiment_submission_dataset = xr.merge(evaluation_variable_datasets, compat='no_conflicts', join='outer')
        experiment_submission_datasets[experiment_submission.name] =  experiment_submission_dataset
        missing_files[experiment_submission.name] = submission_missing_files
    return experiment_submission_datasets, missing_files

def regrid_dataset(src: xr.Dataset, target_grid: xr.Dataset, sample_dims: list[str] | None=None, **regridder_kwargs) -> xr.Dataset:
    """Regrid dataset to target grid. Sample dimensions are those not part of the grid."""
    if sample_dims is not None:
        indexer = {sample_dim: 0 for sample_dim in sample_dims}
        src_no_sample_dims = src.isel(**indexer).squeeze()
    else:
        src_no_sample_dims = src
    regridder = xesmf.Regridder(src_no_sample_dims, target_grid, **regridder_kwargs)
    regridded = regridder.regrid_dataset(src)
    return transfer_attrs(src, regridded)

def transfer_attrs(src: xr.Dataset, dst: xr.Dataset) -> xr.Dataset:
    for var in dst.data_vars:
        if var in src.data_vars:
            dst[var] = dst[var].assign_attrs(src[var].attrs)
    dst = dst.assign_attrs(src.attrs)
    return dst

def compute_huss_from_tdas(tdas: xr.DataArray, ps: xr.DataArray) -> xr.DataArray:
    """Compute huss from tdas.
    
    Compute near-surface specific humidity ('huss') from near-surface dewpoint temperature
    ('tdas') and surface pressure ('ps'). Needed because ERA5 data provides 'tdas', whereas
    CMIP requires 'huss'. See below for formula:
    https://prod.ecmwf-forum-prod.compute.cci2.ecmwf.int/t/how-to-calculate-hus-at-2m-huss/1254

    Args:
        tdas: near-surface dewpoint temperature in K.
        ps: surface pressure in Pa.
        
    Returns:
        Near-surface specific humidity in kg/kg
    """
    Rdry = 287.0597
    Rvap = 461.5250
    a1 = 611.21
    a2 = 273.16
    a3 = 17.502
    a4 = 32.19
    E = a1 * np.exp(a3 * (tdas - a2) / (tdas - a4)) # saturation vapor pressure at dewpoint (Teten's formula)
    huss = (Rdry / Rvap) * E / (ps - ((1 - Rdry / Rvap) * E))
    huss = huss.assign_attrs({'long_name': 'near-surface specific humidity', 'units': '1'})
    return huss

def convert_tdas_to_huss(ds: xr.Dataset) -> xr.Dataset:
    if 'tdas' and 'ps' in ds.data_vars and 'huss' not in ds.data_vars:
        print("Converting 'tdas' to 'huss'.")
        ds['huss'] = compute_huss_from_tdas(ds['tdas'], ds['ps'])
        return ds.drop_vars(['tdas'])
    elif 'huss' not in ds.data_vars:
        print("No 'tdas' or 'ps' available to calculate 'huss'.")
    else:
        print("'huss' already present in dataset.")
    return ds