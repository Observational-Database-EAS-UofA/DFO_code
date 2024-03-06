import os
import xarray as xr
import numpy as np
import pandas as pd

from bot_rd_DFO import bot_rd_DFO
from ctd_rd_DFO import ctd_rd_DFO
from che_rd_DFO import che_rd_DFO


def add_nan_to_data(data, max_length):
    for i in range(len(data)):
        diff = max_length - len(data[i])
        if diff > 0:
            data[i] = np.pad(data[i], (0, diff), mode='constant', constant_values=np.nan)


def get_max_len(data_list):
    longest_list_index = np.argmax([len(sub_list) for sub_list in data_list])
    return len(data_list[longest_list_index])


def save_files(data_path, save_path, file_type):
    base_directory = os.getcwd()
    directory = data_path
    os.chdir(directory)

    if file_type == ".ctd":
        files = [f for f in os.listdir() if (f.endswith('.ctd') and (('AT' not in f) and ('WC' not in f)))]
    else:
        files = [f for f in os.listdir() if f.endswith(file_type)]

    filename_list = []
    depth_list = []
    press_list = []
    temp_list = []
    psal_list = []
    mission_list = []
    agency_list = []
    platform_list = []
    type_list = []
    station_list = []
    lon_list = []
    lat_list = []
    start_time_list = []

    netcdf_filename = ''

    for filename in files:
        tempp = None
        print(filename)
        match file_type:
            case ".bot":
                tempp = bot_rd_DFO(filename)
                netcdf_filename = "DFO_2022_bottles_RAW.nc"
            case ".ctd":
                tempp = ctd_rd_DFO(filename)
                netcdf_filename = "DFO_2022_ctd_RAW.nc"
            case ".che":
                tempp = che_rd_DFO(filename)
                netcdf_filename = "DFO_2022_che_RAW.nc"
            case _:
                print("wrong file type")

        filename_list.append(tempp['filename'])
        depth_list.append(tempp['depth'])
        press_list.append(tempp['press'])
        temp_list.append(tempp['temp'])
        psal_list.append(tempp['psal'])
        mission_list.append(tempp['mission'])
        agency_list.append(tempp['agency'])
        platform_list.append(tempp['platform'])
        type_list.append(tempp['type'])
        station_list.append(tempp['station'])
        lon_list.append(tempp['lon'])
        lat_list.append(tempp['lat'])
        start_time_list.append(tempp['start_time'])

    # standardize dataset
    lists = [depth_list, press_list, psal_list, temp_list]
    max_len = max(get_max_len(lst) for lst in lists)
    for lst in lists:
        add_nan_to_data(lst, max_len)

    ds = xr.Dataset(
        coords=dict(
            profile=filename_list,
            level=np.arange(max_len),
            latitude=lat_list,
            longitude=lon_list,
        ),
        data_vars=dict(
            pressure=(["profile", "level"], press_list),
            temperature=(["profile", "level"], temp_list),
            salinity=(["profile", "level"], psal_list),
            depth=(["profile", "level"], depth_list),
            filename=(["profile"], filename_list),
            mission=(["profile"], mission_list),
            agency=(["profile"], agency_list),
            platform=(["profile"], platform_list),
            type=(["profile"], type_list),
            station=(["profile"], station_list),
        )
    )

    os.chdir(base_directory)
    os.chdir(save_path)
    ds.to_netcdf(netcdf_filename)
    os.chdir(base_directory)
