import os
import xarray as xr
import numpy as np
import datetime as dt

from src.functions.rd_DFO import read_DFO


def get_all_data(data_path, save_path, file_type):
    base_directory = os.getcwd()
    directory = data_path
    os.chdir(directory)

    if file_type == ".ctd":
        files = [f for f in os.listdir() if (f.endswith('.ctd') and (('AT' not in f) and ('WC' not in f)))]
    else:
        files = [f for f in os.listdir() if f.endswith(file_type)]

    measurements_attrs = ['depth', 'press', 'temp', 'psal']
    string_attrs = ['chief_scientist', 'platform', 'instrument_type', 'orig_filename', 'orig_header', 'station_no',
                    'datestr', 'time_type', 'timestamp', 'lat', 'lon', 'num_records', 'shallowest_depth',
                    'deepest_depth', 'bottom_depth', ]
    data_lists = {attr: [] for attr in string_attrs + measurements_attrs}

    parent_index = []

    for i, filename in enumerate(files):
        prov = read_DFO(filename)
        for attr in measurements_attrs:
            if attr == 'depth' and len(prov['depth']) == 0:
                data_lists[attr].extend([np.nan] * len(prov['press']))
            elif attr == 'press' and len(prov['press']) == 0:
                data_lists[attr].extend([np.nan] * len(prov['depth']))
            else:
                data_lists[attr].extend(prov[attr])

        for attr in string_attrs:
            data_lists[attr].append(prov[attr])
        create_parent_index(prov, parent_index, i)

    os.chdir("../")
    dataset_name = os.path.basename(os.getcwd())

    ds = xr.Dataset(
        coords=dict(
            timestamp=(['profile'], data_lists['timestamp']),
            lon=(['profile'], data_lists['lon']),
            lat=(['profile'], data_lists['lat']),
        ),
        data_vars=dict(
            chief_scientist=xr.DataArray(data_lists['chief_scientist'], dims=["profile"]),
            platform=xr.DataArray(data_lists['platform'], dims=["profile"]),
            instrument_type=xr.DataArray(data_lists['instrument_type'], dims=["profile"]),
            orig_filename=xr.DataArray(data_lists['orig_filename'], dims=['profile']),
            orig_header=xr.DataArray(data_lists['orig_header'], dims=['profile']),
            station_no=xr.DataArray(data_lists['station_no'], dims=["profile"]),
            datestr=xr.DataArray(data_lists['datestr'], dims=["profile"]),
            parent_index=xr.DataArray(np.concatenate(parent_index), dims=["obs"]),
            num_records=xr.DataArray(data_lists['num_records'], dims=["profile"]),
            bottom_depth=xr.DataArray(data_lists['bottom_depth'], dims=["profile"]),
            shallowest_depth=xr.DataArray(data_lists['shallowest_depth'], dims=["profile"]),
            deepest_depth=xr.DataArray(data_lists['deepest_depth'], dims=["profile"]),
            time_type=xr.DataArray(data_lists['time_type'], dims=["profile"]),

            # measurements
            depth=xr.DataArray(data_lists['depth'], dims=['obs'],
                               attrs=dict(long_name="depth", unit="m", coordinates="time lon lat z")),
            press=xr.DataArray(data_lists['press'], dims=['obs'],
                               attrs=dict(long_name="press", unit="dbar", coordinates="time lon lat z")),
            temp=xr.DataArray(data_lists['temp'], dims=['obs'],
                              attrs=dict(long_name="temp", unit="oC", coordinates="time lon lat z")),
            psal=xr.DataArray(data_lists['psal'], dims=['obs'],
                              attrs=dict(long_name="psal (psu)", unit="psu", coordinates="time lon lat z")),
        ),
        attrs=dict(
            dataset_name=dataset_name,
            creation_date=str(dt.datetime.now().strftime("%Y-%m-%d %H:%M")),
            feature_type="profile"
        )
    )

    print("-" * 100)
    print(ds)

    save_file(file_type, base_directory, save_path, ds)


def save_file(file_type, base_directory, save_path, ds):
    netcdf_filename = ''
    match file_type:
        case ".bot":
            netcdf_filename = "DFO_2022_bottles_RAW.nc"
        case ".ctd":
            netcdf_filename = "DFO_2022_ctd_RAW.nc"
        case ".che":
            netcdf_filename = "DFO_2022_che_RAW.nc"
        case _:
            print("wrong file type")

    os.chdir(base_directory)
    os.chdir("../")
    if save_path not in os.listdir():
        os.mkdir(save_path)
    os.chdir(save_path)
    ds.to_netcdf(netcdf_filename)
    os.chdir(base_directory)


def create_parent_index(data, parent_index, index):
    size = max(len(data['press']), len(data['temp']), len(data['depth']))
    parent_index.append([index] * size)
