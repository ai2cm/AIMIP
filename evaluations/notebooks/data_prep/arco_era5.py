"""Monthly means of hourly 0.25-degree ERA5 from the public ARCO-ERA5 raw mirror.

Worker functions for ERA5-monthly-1deg-ARCO.ipynb. They live in a module so that a process pool can
import them: each task reads one month of one variable at one level and returns its 0.25-degree mean.

The raw mirror has one NetCDF3 file per day, variable and level, holding the day's 24 hourly fields packed
as 16-bit integers (scale_factor, add_offset). Reading whole objects in one batched request per task is
several times faster than reading them through file handles. For months in the daily period, a task also
returns that month's daily means, computed from the same reads.
"""
import functools
import io
import os
import sys

import numpy as np
import scipy.io

ARCO_RAW = 'gs://gcp-public-data-arco-era5/raw'
SURFACE, PRESSURE = 'date-variable-single_level', 'date-variable-pressure_level'
G = 9.80665  # m s-2, geopotential to geopotential height
HOURS_PER_FILE = 24
SHAPE = (HOURS_PER_FILE, 721, 1440)


@functools.lru_cache(maxsize=1)
def _filesystem():
    import fsspec
    return fsspec.filesystem('gs', token='anon')


def raw_path(tree, variable, day, level=None):
    leaf = 'surface.nc' if level is None else f'{level}.nc'
    return f'{ARCO_RAW}/{tree}/{day:%Y/%m/%d}/{variable}/{leaf}'


def _fetch(paths):
    """Whole objects, in the order given, in one batched request."""
    raws = _filesystem().cat(list(paths), batch_size=len(paths), on_error='raise')
    return [raws[p] if p in raws else raws[p.split('://', 1)[1]] for p in paths]  # keys may lack the protocol


def _read(raw):
    """(packed int16 hours, fill value or None, variable) of one raw file.

    A few files hold an extra `expver` axis: ERA5 (1) and its preliminary release ERA5T (5) side by side, each
    hour stored under exactly one of them and the other slice missing (e.g. total_precipitation on 2023-04-01,
    mirrored mid-transition). Those are collapsed to the version present in each hour.
    """
    f = scipy.io.netcdf_file(io.BytesIO(raw), mmap=False)
    (name,) = [v for v in f.variables if v not in ('time', 'latitude', 'longitude', 'expver')]
    var = f.variables[name]
    data = var.data
    fill = getattr(var, '_FillValue', getattr(var, 'missing_value', None))
    if 'expver' in var.dimensions:
        axis = var.dimensions.index('expver')
        present = ~(np.moveaxis(data, axis, 1) == fill).all(axis=(2, 3))  # (hour, expver)
        assert (present.sum(axis=1) == 1).all(), f'{name}: hours with both or neither expver'
        data = np.moveaxis(data, axis, 1)[np.arange(data.shape[0]), present.argmax(axis=1)]
    assert data.shape == SHAPE, data.shape
    return data, fill, var


def unpack(raw):
    """(packed int16 hours, scale_factor, add_offset) of one raw file."""
    data, fill, var = _read(raw)
    if fill is not None:
        assert not np.any(data == fill), 'missing values present'
    return data, float(var.scale_factor), float(var.add_offset)


def unpack_float(raw):
    """Hourly field of one raw file as float64, NaN where missing (e.g. sea surface temperature over land)."""
    packed, fill, var = _read(raw)
    data = float(var.scale_factor) * packed.astype(np.float64) + float(var.add_offset)
    if fill is not None:
        data[packed == fill] = np.nan
    return data


def _sum_hours(raw, hours=slice(None)):
    """Sum over a slice of one file's hours, unpacked: the packing is linear, so sum the integers."""
    data, scale, offset = unpack(raw)
    selected = data[hours]
    return scale * selected.sum(axis=0, dtype=np.int64) + selected.shape[0] * offset


def _day_sums(tree, variable, days, level, kind, next_day):
    """Per day, the sum over its 24 hours of the hourly field (or of the quantity derived from it)."""
    if kind in ('plain', 'zg'):
        return [_sum_hours(raw) for raw in _fetch([raw_path(tree, variable, d, level) for d in days])]
    if kind == 'huss':
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
        import xarray as xr
        from aimip_data_utils import compute_huss_from_tdas
        dewpoint, pressure = variable
        raws = _fetch([raw_path(tree, v, d) for d in days for v in (dewpoint, pressure)])
        sums = []
        for raw_tdas, raw_ps in zip(raws[0::2], raws[1::2]):
            (td, s1, o1), (ps, s2, o2) = unpack(raw_tdas), unpack(raw_ps)
            huss = compute_huss_from_tdas(xr.DataArray(s1 * td.astype(np.float64) + o1),
                                          xr.DataArray(s2 * ps.astype(np.float64) + o2))
            sums.append(huss.values.sum(axis=0))
        return sums
    if kind == 'ts_spec':
        # AIMIP definition of ts: skin temperature over land and sea ice, SST over open ocean. Where SST is
        # defined (ocean), the ice-covered fraction takes skin temperature and the open water SST.
        skin, sst, ice = variable
        raws = _fetch([raw_path(tree, v, d) for d in days for v in (skin, sst, ice)])
        sums = []
        for raw_skin, raw_sst, raw_ice in zip(raws[0::3], raws[1::3], raws[2::3]):
            t_skin, t_sst, c_ice = unpack_float(raw_skin), unpack_float(raw_sst), unpack_float(raw_ice)
            assert not np.isnan(t_skin).any(), 'skin temperature has missing values'
            c_ice = np.where(np.isnan(c_ice), 0.0, c_ice)
            ts = np.where(np.isnan(t_sst), t_skin, c_ice * t_skin + (1 - c_ice) * t_sst)
            sums.append(ts.sum(axis=0))
        return sums
    if kind == 'pr':
        raws = _fetch([raw_path(tree, variable, d) for d in days] + [raw_path(tree, variable, next_day)])
        # a day's accumulation runs from 01 UTC to 00 UTC of the following day
        return [_sum_hours(own, slice(1, None)) + _sum_hours(following, slice(0, 1))
                for own, following in zip(raws[:-1], raws[1:])]
    raise ValueError(kind)


def month_mean(tree, variable, days, level=None, kind='plain', next_day=None, daily=False):
    """0.25-degree monthly mean (721, 1440), latitude from 90 to -90, of one variable at one level.

    kind: 'plain' (mean of the hourly field), 'zg' (geopotential divided by g), 'huss' (variable is the pair
    (2 m dewpoint, surface pressure), converted hourly), 'ts_spec' (variable is the triple (skin temperature,
    SST, sea-ice cover), blended hourly to the AIMIP definition of ts), or 'pr' (hourly accumulated metres of water, each
    covering the hour ending at its time stamp, returned as kg m-2 s-1; needs next_day for the month's last hour).
    With daily=True, also return the daily means (n_days, 721, 1440) as float32; the monthly mean is their mean.
    """
    day_sums = _day_sums(tree, variable, days, level, kind, next_day)
    scale = {'zg': 1 / G, 'pr': 1000.0 / 3600.0}.get(kind, 1.0)  # pr: metres per hour to kg m-2 s-1
    mean = sum(day_sums) * scale / (HOURS_PER_FILE * len(days))
    if not daily:
        return mean
    return mean, np.stack([s * scale / HOURS_PER_FILE for s in day_sums]).astype(np.float32)
