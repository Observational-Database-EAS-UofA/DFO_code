"""
This code reads various data files from DFO_IOS_2022 dataset, processes them, and saves the data in NetCDF format. 
The script can handle different types of files such as '.bot', '.che', and '.ctd'. The processing includes reading 
data, organizing it into an Xarray Dataset, and saving the Dataset as a NetCDF file.
"""

import os
import xarray as xr
import numpy as np
import datetime as dt
from tqdm import tqdm
import sys
from functions.rd_DFO import read_DFO


class DFOReader:
    def __init__(self):
        pass

    def run(self, data_path, save_path, file_type):
        """
        Reads and processes data files from the specified directory.

        Parameters:
        - data_path: Path to the directory containing the data files.
        - save_path: Path to the directory where the processed NetCDF files will be saved.
        - file_type: Type of data files to process (e.g., '.ctd', '.bot', '.che').

        The method reads files, extracts data, and organizes it into lists for creating an Xarray Dataset.
        """
        base_directory = os.getcwd()
        directory = data_path
        os.chdir(directory)

        if file_type == ".ctd":
            files = [
                f
                for f in os.listdir()
                if (f.endswith(".ctd") and (("AT" not in f) and ("WC" not in f)))
            ]
        else:
            files = [f for f in os.listdir() if f.endswith(file_type)]

        measurements_attrs = ["depth", "press", "temp", "psal"]
        string_attrs = [
            "cruise_name",
            "chief_scientist",
            "platform",
            "instrument_type",
            "orig_filename",
            "orig_header",
            "station_no",
            "datestr",
            "timezone",
            "timestamp",
            "lat",
            "lon",
            "num_records",
            "shallowest_depth",
            "deepest_depth",
            "bottom_depth",
        ]
        data_lists = {attr: [] for attr in string_attrs + measurements_attrs}

        parent_index = []

        for i, filename in enumerate(tqdm(files)):
            prov = read_DFO(filename)
            for attr in measurements_attrs:
                if attr == "depth" and len(prov["depth"]) == 0:
                    data_lists[attr].extend([np.nan] * len(prov["press"]))
                elif attr == "press" and len(prov["press"]) == 0:
                    data_lists[attr].extend([np.nan] * len(prov["depth"]))
                else:
                    data_lists[attr].extend(prov[attr])

            for attr in string_attrs:
                data_lists[attr].append(prov[attr])
            self.create_parent_index(prov, parent_index, i)

        os.chdir("../")
        ds = self.create_dataset(data_lists, parent_index, string_attrs)
        self.save_file(file_type, base_directory, save_path, ds)

    def create_dataset(self, data_lists, parent_index, string_attrs):
        """
        Creates an Xarray Dataset from the processed data.

        Parameters:
        - data_lists: Dictionary containing lists of data for each attribute.
        - parent_index: List of parent-child indices for the data.
        - string_attrs: List of string attributes to include in the Dataset.

        Returns:
        - ds: An Xarray Dataset containing the processed data.
        """
        ds = xr.Dataset(
            coords=dict(
                timestamp=(["profile"], data_lists["timestamp"]),
                lon=(["profile"], data_lists["lon"]),
                lat=(["profile"], data_lists["lat"]),
            ),
            data_vars=dict(
                {
                    **{
                        attr: xr.DataArray(data_lists[attr], dims=["profile"])
                        for attr in string_attrs
                        if attr not in ["timestamp", "lon", "lat"]
                    },
                },
                parent_index=xr.DataArray(np.concatenate(parent_index), dims=["obs"]),
                # measurements
                depth=xr.DataArray(
                    data_lists["depth"],
                    dims=["obs"],
                    attrs=dict(
                        long_name="depth", unit="m", coordinates="time lon lat z"
                    ),
                ),
                press=xr.DataArray(
                    data_lists["press"],
                    dims=["obs"],
                    attrs=dict(
                        long_name="press", unit="dbar", coordinates="time lon lat z"
                    ),
                ),
                temp=xr.DataArray(
                    data_lists["temp"],
                    dims=["obs"],
                    attrs=dict(
                        long_name="temp", unit="oC", coordinates="time lon lat z"
                    ),
                ),
                psal=xr.DataArray(
                    data_lists["psal"],
                    dims=["obs"],
                    attrs=dict(
                        long_name="psal (psu)", unit="psu", coordinates="time lon lat z"
                    ),
                ),
            ),
            attrs=dict(
                dataset_name="DFO_IOS_2022",
                creation_date=str(dt.datetime.now().strftime("%Y-%m-%d %H:%M")),
                feature_type="profile",
            ),
        )

        return ds

    def save_file(self, file_type, base_directory, save_path, ds):
        print(f"saving {file_type} file... it may take a few minutes.")
        netcdf_filename = ""
        match file_type:
            case ".bot":
                netcdf_filename = "DFO_2022_bottles_RAW.nc"
            case ".ctd":
                netcdf_filename = "DFO_2022_ctd_RAW.nc"
            case ".che":
                netcdf_filename = "DFO_2022_che_RAW.nc"
            case _:
                print(f"{file_type} is not a valid file type")

        os.chdir(base_directory)
        os.chdir("../")
        if not os.path.isdir(save_path):
            os.mkdir(save_path)
        os.chdir(save_path)
        ds.to_netcdf(netcdf_filename, unlimited_dims={"obs": True})
        os.chdir(base_directory)

    def create_parent_index(self, data, parent_index, index):
        size = max(len(data["press"]), len(data["temp"]), len(data["depth"]))
        parent_index.append([index] * size)


def main(data_path, save_path):
    dfo_reader = DFOReader()

    for file_type in [".bot", ".che", ".ctd"]:
        dfo_reader.run(data_path, save_path, file_type)


if __name__ == "__main__":
    original_data_path = "/mnt/storage6/caio/AW_CAA/CTD_DATA/DFO_IOS_2022/original_data"
    save_path = "/mnt/storage6/caio/AW_CAA/CTD_DATA/DFO_IOS_2022/ncfiles_raw"
    main(original_data_path, save_path)
