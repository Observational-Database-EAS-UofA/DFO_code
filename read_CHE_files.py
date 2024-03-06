import xarray as xr


def read_file():
    with xr.open_dataset("ncfiles/DFO_2022_bottles_RAW.nc") as ds:
        # print(ds)
        for p in ds['pressure']:
            for j in xr.DataArray(p):
                print(j)
