import os
import xarray as xr
import numpy as np

from src.functions.rd_DFO import read_DFO


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
    header_list = []
    depth_list = []
    press_list = []
    temp_list = []
    psal_list = []
    mission_list = []
    agency_list = []
    platform_list = []
    instrument_type_list = []
    station_list = []
    lon_list = []
    lat_list = []
    num_records_list = []
    water_depth_list = []
    datestr_list = []
    serialtime_list = []

    for filename in files:
        temp = read_DFO(filename)

        filename_list.append(temp['filename'])
        header_list.append(temp['header'])
        depth_list.append(temp['depth'])
        press_list.append(temp['press'])
        temp_list.append(temp['temp'])
        psal_list.append(temp['psal'])
        mission_list.append(temp['mission'])
        agency_list.append(temp['agency'])
        platform_list.append(temp['platform'])
        instrument_type_list.append(temp['type'])
        station_list.append(temp['station'])
        lon_list.append(temp['lon'])
        lat_list.append(temp['lat'])
        num_records_list.append(temp['number_of_records'])
        water_depth_list.append(temp['water_depth'])
        datestr_list.append(temp['datestr'])
        serialtime_list.append(temp['serial_time'])

    # standardize dataset
    lists = [depth_list, press_list, psal_list, temp_list]
    max_len = max(get_max_len(lst) for lst in lists)
    for lst in lists:
        add_nan_to_data(lst, max_len)

    os.chdir("../")
    dataset_name = os.path.basename(os.getcwd())

    ds = xr.Dataset(
        coords=dict(
            profile=filename_list,
            level=np.arange(max_len),
            latitude=lat_list,
            longitude=lon_list,
        ),
        data_vars=dict(
            dataset_name=dataset_name,
            orig_filename=(["profile"], filename_list),
            orig_header=(["profile"], header_list),
            mission=(["profile"], mission_list),
            agency=(["profile"], agency_list),
            platform=(["profile"], platform_list),
            type=(["profile"], instrument_type_list),
            station=(["profile"], station_list),
            pressure=(["profile", "level"], press_list),
            temperature=(["profile", "level"], temp_list),
            salinity=(["profile", "level"], psal_list),
            depth=(["profile", "level"], depth_list),
            instrument_type=(["profile"], instrument_type_list),
            num_records=(["profile"], num_records_list),
            datestr=(["profile"], datestr_list),
            serialtime=(["profile"], serialtime_list)
        )
    )

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
    if save_path not in os.listdir():
        os.mkdir(save_path)
    os.chdir(save_path)
    ds.to_netcdf(netcdf_filename)
    os.chdir(base_directory)
