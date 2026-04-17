import xarray as xr
import numpy as np
import xesmf
import healpy as hp
import fsspec
import os
from copy import deepcopy
import dataclasses
from matplotlib import pyplot as plt
from typing import Literal

DATA_ROOT = os.environ.get('AIMIP_DATA_ROOT', '../../local_data')
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
DEFAULT_TIME_LABELS = {
    'all_months': '197810-202412',
    'daily_first_15_months': '19781001-19791231',
    'daily_last_12_months': '20240101-20241231',
}

ACE_FILE_TEMPLATE = 'r{i_r}i1p1f1/{table}/{varname}/{grid}/{label}/{varname}_{table}_ACE2-ERA5_{experiment_name}_r{i_r}i1p1f1_{grid}_{time_period}.nc'
ARCHES_WEATHER_AIMIP_FILE_TEMPLATE = 'r{i_r}i1p1f1/{table}/{varname}/{grid}/{varname}_{table}_ArchesWeather_{experiment_name}_r{i_r}i1p1f1_{grid}_{time_period}.nc'
ARCHES_WEATHER_AIMIP_PK_FILE_TEMPLATE = 'r{i_r}i1p1f1/{table}/{varname}/{grid}/{varname}_{table}_ArchesWeather_aimip_r{i_r}i1p1f1_{grid}_{time_period}.nc'
ARCHES_WEATHER_GEN_FILE_TEMPLATE = 'r{i_r}i1p1f1/{table}/{varname}/{grid}/{varname}_{table}_ArchesWeatherGen_{experiment_name}_r{i_r}i1p1f1_{grid}_{time_period}.nc'
DLESYM_FILE_TEMPLATE = 'r{i_r}i1p1f1/{table}/{varname}/{grid}/{label}/{varname}_{table}_DLESyM_{experiment_name}_r{i_r}i1p1f1_{grid}_{time_period}.nc'
NEURAL_GCM_FILE_TEMPLATE = 'r{i_r}i1p1f1/{table}/{varname}/{grid}/{label}/{varname}_{table}_NeuralGCM_{experiment_name}_r{i_r}i1p1f1_{grid}_{time_period}.nc'
NEURAL_GCM_HRD_FILE_TEMPLATE = 'r{i_r}i1p1f1/{table}/{varname}/{grid}/{label}/{varname}_{table}_NeuralGCM-HRD_{experiment_name}_r{i_r}i1p1f1_{grid}_{time_period}.nc'
CBOTTLE_FILE_TEMPLATE = 'r1i1p{i_r}f1/{table}/{varname}/{grid}/{label}/{varname}_{table}_cBottle-1-3_{experiment_name}_r1i1p{i_r}f1_{grid}_{time_period}.nc'
MD_FILE_TEMPLATE = 'r{i_r}i1p1f1/{table}/{varname}/{grid}/{label}/{varname}_{table}_MD-1p5_{experiment_name}_r{i_r}i1p1f1_{grid}_{time_period}.nc'
ERA5_FILE_TEMLATE = 'mon_1deg/native6_ERA5_an_v1_Amon_{varname}_1978-2024.nc'
GFDL_CM4_AMIP_ZARR_TEMPLATE = 'gs://cmip6/CMIP6/CMIP/NOAA-GFDL/GFDL-CM4/amip/r1i1p1f1/Amon/{varname}/gr1/v20180701'
GFDL_CM4_AMIP_DAILY_ZARR_TEMPLATE = 'gs://cmip6/CMIP6/CMIP/NOAA-GFDL/GFDL-CM4/amip/r1i1p1f1/day/{varname}/gr1/v20180701'

FILE_TEMPLATES = {
    'ACE2.1-ERA5-aimip': ACE_FILE_TEMPLATE,
    'ACE2.1-ERA5-aimip-p2k': ACE_FILE_TEMPLATE,
    'ACE2.1-ERA5-aimip-p4k': ACE_FILE_TEMPLATE,
    'ArchesWeather-V2-aimip': ARCHES_WEATHER_AIMIP_FILE_TEMPLATE,
    'ArchesWeather-V2-aimip-p2k': ARCHES_WEATHER_AIMIP_PK_FILE_TEMPLATE,
    'ArchesWeather-V2-aimip-p4k': ARCHES_WEATHER_AIMIP_PK_FILE_TEMPLATE,
    'ArchesWeatherGen-V2-aimip': ARCHES_WEATHER_GEN_FILE_TEMPLATE,
    'ArchesWeatherGen-V2-aimip-p2k': ARCHES_WEATHER_GEN_FILE_TEMPLATE,
    'ArchesWeatherGen-V2-aimip-p4k': ARCHES_WEATHER_GEN_FILE_TEMPLATE,
    'DLESyM-aimip': DLESYM_FILE_TEMPLATE,
    'DLESyM-aimip-p2k': DLESYM_FILE_TEMPLATE,
    'DLESyM-aimip-p4k': DLESYM_FILE_TEMPLATE,
    'NeuralGCM-aimip': NEURAL_GCM_FILE_TEMPLATE,
    'NeuralGCM-aimip-p2k': NEURAL_GCM_FILE_TEMPLATE,
    'NeuralGCM-aimip-p4k': NEURAL_GCM_FILE_TEMPLATE,
    'NeuralGCM-HRD-aimip': NEURAL_GCM_HRD_FILE_TEMPLATE,
    'NeuralGCM-HRD-aimip-p2k': NEURAL_GCM_HRD_FILE_TEMPLATE,
    'NeuralGCM-HRD-aimip-p4k': NEURAL_GCM_HRD_FILE_TEMPLATE,
    'cBottle1.3-aimip': CBOTTLE_FILE_TEMPLATE,
    'cBottle1.3-aimip-p2k': CBOTTLE_FILE_TEMPLATE,
    'cBottle1.3-aimip-p4k': CBOTTLE_FILE_TEMPLATE,
    'MD1.5-aimip': MD_FILE_TEMPLATE,
    'MD1.5-aimip-2k': MD_FILE_TEMPLATE,
    'MD1.5-aimip-4k': MD_FILE_TEMPLATE,
    'ERA5': ERA5_FILE_TEMLATE,
}

DEFAULT_GFDL_AM4_CMIP6_VERSION_TAG = 'v20180807'
all_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
CATEGORICAL_COLORS = all_colors[:7] + all_colors[9:]

@dataclasses.dataclass
class EvaluationVariable:
    standard_name: str
    short_name: str
    long_name: str
    units: str 
    standard_pressure_level_indexer: dict[str, list[float]] | None=None
    drop_singleton_pressure_coord: bool=False

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

    def to_standard_pressure_levels(self, ds: xr.Dataset, interpolate_to_pressure_levels: bool) -> xr.Dataset:
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
                    print("Cannot extrapolate to standard pressure levels -- values left missing.")
                if interpolate_to_pressure_levels:
                    ds_out = ds.interp({pressure_dim_name: standard_pressure_levels}, method='linear')
                else:
                    ds_out = (
                        ds
                        .sel({pressure_dim_name: standard_pressure_levels}, method='nearest')
                        .drop_duplicates(pressure_dim_name)
                    )
                if ds_out.sizes[pressure_dim_name] == 1 and self.drop_singleton_pressure_coord:
                    ds_out = ds_out.squeeze().drop_vars(pressure_dim_name)
                return ds_out
            else:
                print(f'Pressure levels specified but no pressure dimension for {self.standard_name}')
        return ds
 
@dataclasses.dataclass
class ExperimentSubmission:
    model_name: str
    submission_dir: str
    experiment_name: str
    label: str | None
    grid: Literal['gr', 'gn']='gn'
    grid_mapping: dict[str, str] | None=None
    renames: dict[str, str] | None=None
    fix_zg: bool=False
    submission_time_labels: dict[str, str] | None=None
    custom_label_mapping: dict[str, str] | None=None
    realization_day_offset: int=0
    data_root: str=DATA_ROOT

    def __post_init__(self):
        if self.experiment_name is None:
            self.experiment_name = ''
        if self.label is None:
            self.label = ''
        if self.renames is None:
            self.renames = {}
        if self.grid_mapping is None:
            self.grid_mapping = {}
        if self.submission_time_labels is None:
            self.submission_time_labels = DEFAULT_TIME_LABELS
        if self.custom_label_mapping is None:
            self.custom_label_mapping = {}

    @property
    def file_template(self) -> str:
        return FILE_TEMPLATES[self.experiment_submission_name]

    @property
    def name(self) -> str:
        return self.model_name

    @property
    def experiment_submission_name(self) -> str:
        if self.experiment_name:
            return f"{self.model_name}-{self.experiment_name}"
        else:
            return self.model_name

    @property
    def reverse_rename(self) -> dict:
        return {v: k for k, v in self.renames.items()}

    def get_grid_for_variable(self, varname: str) -> str:
        if varname in self.grid_mapping:
            return self.grid_mapping[varname]
        else:
            return self.grid

    def get_label(self, table: str, varname: str) -> str:
        if (
            table in self.custom_label_mapping and varname in self.custom_label_mapping[table]
        ):
            return self.custom_label_mapping[table][varname]
        else:
            return self.label
        
    def get_variable_path(
        self,
        variable: EvaluationVariable,
        i_r: int,
        table: str,
        time_period: str,
    ) -> str:
        if variable.short_name in self.renames:
            variable_submission_name = self.renames[variable.short_name]
        else:
            variable_submission_name = variable.short_name
        i_r_day = i_r + self.realization_day_offset
        template = self.submission_time_labels[time_period]
        if isinstance(template, list):
            time_period = template[i_r - 1]
        else:
            time_period = template.format(i_r=i_r, i_r_day=i_r_day)
        file_format = self.file_template.format(
            i_r=i_r,
            table=table,
            varname=variable_submission_name,
            grid=self.get_grid_for_variable(variable.short_name),
            label=self.get_label(table, variable.short_name),
            experiment_name=self.experiment_name,
            time_period=time_period,
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
        model_name='ACE2.1-ERA5',
        submission_dir='Ai2/ACE2-1-ERA5',
        experiment_name='aimip',
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
        model_name='ArchesWeather-V2',
        submission_dir='ArchesWeather/ArchesWeather-V2',
        experiment_name='aimip',
        label=None,
        renames={'ts': 'tos'},
        fix_zg=True,
        submission_time_labels={
            'all_months': '197810-202501',
            'daily_first_15_months': '19781001-19791231',
            'daily_last_12_months': '20240101-20241231',
        },
    ),
    ExperimentSubmission(
        model_name='ArchesWeatherGen-V2',
        submission_dir='ArchesWeather/ArchesWeatherGen-V2',
        experiment_name='aimip',
        label=None,
        renames={'ts': 'tos'},
        fix_zg=True,
        submission_time_labels={
            'all_months': '197810-202501',
            'daily_first_15_months': '19781001-19791231',
            'daily_last_12_months': '20240101-20241231',
        },
    ),
    ExperimentSubmission(
        model_name='cBottle1.3',
        submission_dir='NVIDIA/CMIP6/AIMIP/NVIDIA/cBottle-1-3',
        experiment_name='aimip',
        label='v20260323',
        fix_zg=True,
    ),
    ExperimentSubmission(
        model_name='DLESyM',
        submission_dir='DLESyM/DLESyM',
        experiment_name='aimip',
        grid='gn',
        label='v20260406',
        realization_day_offset=2,
        submission_time_labels={
            'all_months': [
                '19781016-20241216',  # r1
                '19781016-20241216',  # r2
                '19781016-20241216',  # r3
                '19781016-20241216',  # r4
                '19781016-20250116',  # r5
            ],
            'daily_first_15_months': '1978100{i_r_day}-19841231',
        }
    ),
    ExperimentSubmission(
        model_name='MD1.5',
        submission_dir='UMD-PARETO/MD-1p5',
        experiment_name='aimip',
        grid='gr',
        label='v20251217',
        fix_zg=True,
    ),
    ExperimentSubmission(
        model_name='NeuralGCM',
        submission_dir='Google/NeuralGCM',
        experiment_name='aimip',
        label='v20260304',
        custom_label_mapping={
            'day': {
                'hus': 'v20260306',
                'ps': 'v20260306',
                'ta': 'v20260306',
                'tas': 'v20260306',
                'tdas': 'v20260306',
                'ts': 'v20260306',
                'ua': 'v20260306',
                'uas': 'v20260306',
                'va': 'v20260306',
                'vas': 'v20260306',
                'zg': 'v20260306',
            },
        },
        fix_zg=True,
    ),
    ExperimentSubmission(
        model_name='NeuralGCM-HRD',
        submission_dir='Google/NeuralGCM-HRD',
        experiment_name='aimip',
        label='v20260304',
        custom_label_mapping={
            'day': {
                'hus': 'v20260306',
                'ps': 'v20260305',
                'ta': 'v20260306',
                'tas': 'v20260305',
                'tdas': 'v20260305',
                'ts': 'v20260305',
                'ua': 'v20260306',
                'uas': 'v20260305',
                'va': 'v20260306',
                'vas': 'v20260305',
                'zg': 'v20260306',
            },
        },
        fix_zg=True,
    ),
]

ERA5_1DEG = ExperimentSubmission(
    model_name='ERA5',
    submission_dir='ERA5',
    experiment_name=None,
    label=None,
)

AIMIP_P2K_EXPERIMENT_SUBMISSIONS = [
    ExperimentSubmission(
        model_name='ACE2.1-ERA5',
        submission_dir='Ai2/ACE2-1-ERA5',
        experiment_name='aimip-p2k',
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
        model_name='ArchesWeather-V2',
        submission_dir='ArchesWeather/ArchesWeather-V2',
        experiment_name='aimip-p2k',
        label=None,
        renames={'ts': 'tos'},
        fix_zg=True,
        submission_time_labels={
            'all_months': '197810-202501',
            'daily_first_15_months': '19781001-19791231',
            'daily_last_12_months': '20240101-20241231',
        },
    ),
    ExperimentSubmission(
        model_name='ArchesWeatherGen-V2',
        submission_dir='ArchesWeather/ArchesWeatherGen-V2',
        experiment_name='aimip-p2k',
        label=None,
        renames={'ts': 'tos'},
        fix_zg=True,
        submission_time_labels={
            'all_months': '197810-202501',
            'daily_first_15_months': '19781001-19791231',
            'daily_last_12_months': '20240101-20241231',
        },
    ),
    ExperimentSubmission(
        model_name='cBottle1.3',
        submission_dir='NVIDIA/CMIP6/AIMIP/NVIDIA/cBottle-1-3',
        experiment_name='aimip-p2k',
        label='v20260323',
        fix_zg=True,
    ),
    ExperimentSubmission(
        model_name='DLESyM',
        submission_dir='DLESyM/DLESyM',
        experiment_name='aimip-p2k',
        grid='gn',
        label='v20260406',
        realization_day_offset=2,
        submission_time_labels={
            'all_months': [
                '19781016-20241216',  # r1
                '19781016-20241216',  # r2
                '19781016-20241216',  # r3
                '19781016-20241216',  # r4
                '19781016-20250116',  # r5
            ],
            'daily_first_15_months': '1978100{i_r_day}-19841231',
        }
    ),
    ExperimentSubmission(
        model_name='MD1.5',
        submission_dir='UMD-PARETO/MD-1p5',
        experiment_name='aimip-2k',
        grid='gr',
        label='v20251217',
        fix_zg=True,
    ),
    ExperimentSubmission(
        model_name='NeuralGCM',
        submission_dir='Google/NeuralGCM',
        experiment_name='aimip-p2k',
        label='v20260304',
        fix_zg=True,
    ),
    ExperimentSubmission(
        model_name='NeuralGCM-HRD',
        submission_dir='Google/NeuralGCM-HRD',
        experiment_name='aimip-p2k',
        label='v20260304',
        fix_zg=True,
    ),
]

AIMIP_P4K_EXPERIMENT_SUBMISSIONS = [
    ExperimentSubmission(
        model_name='ACE2.1-ERA5',
        submission_dir='Ai2/ACE2-1-ERA5',
        experiment_name='aimip-p4k',
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
        model_name='ArchesWeather-V2',
        submission_dir='ArchesWeather/ArchesWeather-V2',
        experiment_name='aimip-p4k',
        label=None,
        renames={'ts': 'tos'},
        fix_zg=True,
        submission_time_labels={
            'all_months': '197810-202501',
            'daily_first_15_months': '19781001-19791231',
            'daily_last_12_months': '20240101-20241231',
        },
    ),
    ExperimentSubmission(
        model_name='ArchesWeatherGen-V2',
        submission_dir='ArchesWeather/ArchesWeatherGen-V2',
        experiment_name='aimip-p4k',
        label=None,
        renames={'ts': 'tos'},
        fix_zg=True,
        submission_time_labels={
            'all_months': '197810-202501',
            'daily_first_15_months': '19781001-19791231',
            'daily_last_12_months': '20240101-20241231',
        },
    ),
    ExperimentSubmission(
        model_name='cBottle1.3',
        submission_dir='NVIDIA/CMIP6/AIMIP/NVIDIA/cBottle-1-3',
        experiment_name='aimip-p4k',
        label='v20260323',
        fix_zg=True,
    ),
    ExperimentSubmission(
        model_name='DLESyM',
        submission_dir='DLESyM/DLESyM',
        experiment_name='aimip-p4k',
        grid='gn',
        label='v20260406',
        realization_day_offset=2,
        submission_time_labels={
            'all_months': [
                '19781016-20241216',  # r1
                '19781016-20241216',  # r2
                '19781016-20241216',  # r3
                '19781016-20241216',  # r4
                '19781016-20250116',  # r5
            ],
            'daily_first_15_months': '1978100{i_r_day}-19841231',
        }
    ),
    ExperimentSubmission(
        model_name='MD1.5',
        submission_dir='UMD-PARETO/MD-1p5',
        experiment_name='aimip-4k',
        grid='gr',
        label='v20251217',
        fix_zg=True,
    ),
    ExperimentSubmission(
        model_name='NeuralGCM',
        submission_dir='Google/NeuralGCM',
        experiment_name='aimip-p4k',
        label='v20260304',
        fix_zg=True,
    ),
    ExperimentSubmission(
        model_name='NeuralGCM-HRD',
        submission_dir='Google/NeuralGCM-HRD',
        experiment_name='aimip-p4k',
        label='v20260304',
        fix_zg=True,
    ),
]

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
        drop_singleton_pressure_coord=True
    ),
]

def open_variable_from_path(
    path: str,
    evaluation_variable: EvaluationVariable,
    experiment_submission: ExperimentSubmission,
    template: xr.Dataset,
) -> tuple[xr.Dataset, bool]:
    try:
        variable_dataset = xr.open_dataset(path, chunks={})
    except FileNotFoundError:
        print(f"Not found: {path}")
        variable_dataset = xr.full_like(template, fill_value=np.nan)
        missing = True
    else:
        print(path)
        missing = False
        if evaluation_variable.short_name == 'zg':
            pressure_interp = False
        elif evaluation_variable.short_name == 'ta' and experiment_submission.submission_dir == 'DLESyM/DLESyM':
            pressure_interp = False
        else:
            pressure_interp = True
        variable_dataset = (
            variable_dataset
            .pipe(experiment_submission.rename_variable)
            .pipe(experiment_submission.apply_zg_fix)
            .pipe(evaluation_variable.validate_metadata)
            .pipe(evaluation_variable.to_standard_pressure_levels, pressure_interp)
        )
    # singleton height coordinate for surface variables causes xarray merge conflicts
    variable_dataset = variable_dataset.drop_vars("height", errors="ignore") 
    return variable_dataset, missing

def open_aimip_data(
    experiment_submissions: list[ExperimentSubmission],
    evaluation_variables: list[EvaluationVariable],
    table: Literal['Amon', 'day'],
    time_period: Literal['all_months', 'daily_first_15_months', 'daily_last_12_months']='all_months',
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
            template = xr.Dataset()
            for i_r in range(1, n_realizations + 1):
                variable_path = experiment_submission.get_variable_path(evaluation_variable, i_r, table, time_period)
                realization_dataset, missing = open_variable_from_path(variable_path, evaluation_variable, experiment_submission, template)
                realization_datasets.append(realization_dataset.expand_dims({'realization': [i_r]}))
                if missing:
                    submission_missing_files.append(variable_path)
                else:
                    template = realization_dataset
            evaluation_variable_dataset = xr.concat(realization_datasets, dim='realization', compat='no_conflicts', join='inner')
            evaluation_variable_datasets.append(evaluation_variable_dataset)
        experiment_submission_dataset = xr.merge(evaluation_variable_datasets, compat='no_conflicts', join='outer')
        experiment_submission_datasets[experiment_submission.name] =  experiment_submission_dataset
        missing_files[experiment_submission.name] = submission_missing_files
    return experiment_submission_datasets, missing_files

def add_latlon_to_dlesym(
    dlesm_ds: xr.Dataset,
    nside: int=64,
    face_dim: str='face', 
    width_dim: str='width', 
    height_dim: str='height', 
    lat_name: str='lat',
    lon_name: str='lon',
    ipix_name: str='i',    
) -> xr.Dataset:
    
    """Add lat and lon variables to the DLESyM HEALPix dataset.
    
    DLESyM dataset is missing lat/lon coords; it has only face/height/width coords.
    With healpy, compute these variables from the sizes of these coords, and add
    them to the dataset as variables (not coords). Also stack the dataset along
    a cell dimension for easier regridding.
    """

    dlesm_ds_out = deepcopy(dlesm_ds) # don't mutate input

    assert dlesm_ds_out.sizes[height_dim] == nside, "height dim size"
    assert dlesm_ds_out.sizes[width_dim] == nside, "width dim size"
    assert dlesm_ds_out.sizes[face_dim] == 12, "face dim size"

    F, Y, X = xr.broadcast(
        dlesm_ds_out[face_dim], dlesm_ds_out[height_dim], dlesm_ds_out[width_dim],
    )
    ipix = hp.xyf2pix(64, X.values, Y.values, F.values, nest=False)
    lon, lat = hp.pix2ang(nside, ipix, lonlat=True, nest=False)

    # for some reason this is needed to map to the DLESyM variables properly
    lon = lon[:, ::-1, ::-1]
    lat = lat[:, ::-1, ::-1]

    # assign as variables
    dlesm_ds_out[lon_name] = xr.DataArray(lon, dims=[face_dim, width_dim, height_dim])
    dlesm_ds_out[lat_name] = xr.DataArray(lat, dims=[face_dim, width_dim, height_dim])
    dlesm_ds_out[ipix_name] = xr.DataArray(ipix, dims=[face_dim, width_dim, height_dim])

    # stack along ipix dim
    dlesm_ds_out = dlesm_ds_out.stack({"cell": [face_dim, width_dim, height_dim]})
    dlesm_ds_out = dlesm_ds_out.sortby(ipix_name)
    dlesm_ds_out = dlesm_ds_out.drop_vars(["cell", face_dim, width_dim, height_dim]).rename({"cell": ipix_name})
    return dlesm_ds_out

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

def compute_time_mean(ds: xr.Dataset, start: str, end: str, time_dim_name: str='time') -> xr.Dataset:
    time_subset = ds.sel(**{time_dim_name: slice(start, end)})
    with xr.set_options(keep_attrs=True):
        return time_subset.mean(time_dim_name)

def compute_rms(field: xr.Dataset, lat_dim: str='lat', lon_dim: str='lon') -> xr.Dataset:
    weights = np.cos(np.deg2rad(field[lat_dim]))
    rms = np.sqrt((field ** 2).weighted(weights).mean(dim=[lat_dim, lon_dim]))
    rms = transfer_attrs(field, rms)
    return rms

def compute_weighted_mean(field: xr.Dataset, lat_dim: str='lat', lon_dim: str='lon') -> xr.Dataset:
    weights = np.cos(np.deg2rad(field[lat_dim]))
    mean = field.weighted(weights).mean(dim=[lat_dim, lon_dim])
    mean = transfer_attrs(field, mean)
    return mean

def compute_error(pred: xr.Dataset, target: xr.Dataset) -> xr.Dataset:
    error = pred - target
    error = transfer_attrs(pred, error)
    return error

def open_variable_from_cmip6_gcs_zarr(
    path: str,
    evaluation_variable: EvaluationVariable,
) -> tuple[xr.Dataset, bool]:
    try:
        variable_dataset = xr.open_zarr(path)
    except FileNotFoundError:
        print(f"Not found: {path}")
        missing = True
        variable_dataset = xr.Dataset()
    else:
        print(path)
        missing = False
        variable_dataset = evaluation_variable.to_standard_pressure_levels(
            variable_dataset, interpolate_to_pressure_levels=False
        )
    # singleton height coordinate for surface variables causes xarray merge conflicts
    variable_dataset = variable_dataset.drop_vars("height", errors="ignore") 
    return variable_dataset, missing

def load_gfdl_am4_from_cmip6_gcs(
    zarr_template: str,
    eval_variables: list[EvaluationVariable],
    other_variables: list[str],
    version_tag_mapping: dict[str, str] | None=None,
) -> tuple[xr.Dataset, list[str]]:
    root_dir = zarr_template.format(
        varname=eval_variables[0].short_name, version_tag=DEFAULT_GFDL_AM4_CMIP6_VERSION_TAG
    ).split(eval_variables[0].short_name)[0]
    fs, *_ = fsspec.get_fs_token_paths(root_dir)
    all_variables = [os.path.basename(path) for path in fs.ls(root_dir)]
    eval_variables_shortname = [eval_variable.short_name for eval_variable in eval_variables]
    available_variables = list(set(all_variables).intersection(set(eval_variables_shortname)))
    default_version_tag_mapping = {
        k: DEFAULT_GFDL_AM4_CMIP6_VERSION_TAG for k in available_variables
    }
    if version_tag_mapping is not None:
        version_tag_mapping = {**default_version_tag_mapping, **version_tag_mapping}
    else:
        version_tag_mapping = default_version_tag_mapping
    ds_out = xr.Dataset()
    missing_paths = []
    for eval_variable in [
        eval_variable for eval_variable in eval_variables if eval_variable.short_name in available_variables
    ]:
        varname = eval_variable.short_name
        zarrpath = zarr_template.format(varname=varname, version_tag=version_tag_mapping[varname])
        var_ds, missing = open_variable_from_cmip6_gcs_zarr(zarrpath, eval_variable)
        if missing:
            missing_paths.append(zarrpath)
        ds_out[varname] = var_ds[varname]
        for other_varname in other_variables:
            if other_varname not in ds_out.data_vars and other_varname in var_ds:
                ds_out[other_varname] = var_ds[other_varname]
    ds_out = ds_out.assign_attrs(var_ds.attrs)
    return ds_out, missing_paths
