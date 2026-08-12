import numpy as np
import xarray as xr

from aimip_data_utils import compute_huss_from_tdas, convert_tdas_to_huss


def make_dataset(**variables: float) -> xr.Dataset:
    """Single-timestep dataset with one scalar value per named variable."""
    return xr.Dataset(
        {name: ('time', np.array([value])) for name, value in variables.items()}
    )


def test_compute_huss_from_tdas():
    # 280 K dewpoint at 1000 hPa is about 6.2 g/kg of water vapor.
    huss = compute_huss_from_tdas(
        make_dataset(tdas=280.0)['tdas'], make_dataset(ps=1.0e5)['ps']
    )
    np.testing.assert_allclose(huss.values, 0.006186, rtol=1e-3)
    assert huss.attrs['units'] == '1'


def test_convert_tdas_to_huss_converts_when_tdas_and_ps_present():
    ds = make_dataset(tdas=280.0, ps=1.0e5)
    converted = convert_tdas_to_huss(ds)
    assert 'tdas' not in converted.data_vars
    np.testing.assert_allclose(converted['huss'].values, 0.006186, rtol=1e-3)


def test_convert_tdas_to_huss_without_tdas():
    ds = make_dataset(ps=1.0e5)
    converted = convert_tdas_to_huss(ds)
    assert list(converted.data_vars) == ['ps']


def test_convert_tdas_to_huss_without_ps():
    ds = make_dataset(tdas=280.0)
    converted = convert_tdas_to_huss(ds)
    assert list(converted.data_vars) == ['tdas']


def test_convert_tdas_to_huss_keeps_submitted_huss():
    ds = make_dataset(huss=0.008, tdas=280.0, ps=1.0e5)
    converted = convert_tdas_to_huss(ds)
    np.testing.assert_allclose(converted['huss'].values, 0.008)
    assert 'tdas' in converted.data_vars
