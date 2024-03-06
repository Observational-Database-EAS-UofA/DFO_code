import numpy as np
import pandas as pd
from shared.reader import read_table_vertically


def che_rd_DFO(cnv_file, FMT='IR'):
    header_str = ''
    mission = None
    agency = None
    platform = None
    type_ = None
    station = None
    lat = None
    lon = None
    start_time = None

    # Read the header.
    no_channels = 0
    depthvar = None
    pressvar = None
    tempvar = None
    salvar = None

    with open(cnv_file, 'r', errors="ignore") as fid:
        print(cnv_file)
        line = '*START'
        m = 0
        while '*END OF HEADER' not in line:
            line = fid.readline()
            m = m + 1
            header_str += line
            first_of_line = line.split(":")[0].strip()
            if ' NUMBER OF CHANNELS ' in line:
                no_channels = int(line.split(':')[1].strip())
                line = fid.readline()
                m = m + 1
                line = fid.readline()
                m = m + 1

            if ' $TABLE: CHANNELS' in line:
                line = fid.readline()
                m = m + 1
                line = fid.readline()
                m = m + 1
                for mm in range(no_channels):
                    line = fid.readline()
                    m = m + 1
                    if 'Depth' in line:
                        depthvar = mm
                    elif ' Pressure' in line:
                        pressvar = mm
                    elif ' Temperature' in line:
                        tempvar = mm
                    elif ' Salinity' in line:
                        salvar = mm

            elif 'MISSION' == first_of_line:
                mission = line.split(':')[1].strip()

            elif 'AGENCY' == first_of_line:
                agency = line.split(':')[1].strip()

            elif 'PLATFORM' == first_of_line or 'SCIENTIST' == first_of_line or 'PROJECT' == first_of_line:
                platform = line.split(':')[1].strip()

            elif 'TYPE' == first_of_line:
                type_ = line.split(':')[1].strip()

            elif 'STATION' == first_of_line:
                station = line.split(':')[1].strip()

            elif 'LATITUDE' == first_of_line:
                lat_str = line.split(':')[1].strip().split()
                lat_deg = float(lat_str[0])
                lat_min = float(lat_str[1])
                lat = lat_deg + lat_min / 60

            elif 'LONGITUDE' == first_of_line:
                lon_str = line.split(':')[1].strip().split()
                lon_deg = float(lon_str[0])
                lon_min = float(lon_str[1])
                lon = -1 * (lon_deg + lon_min / 60)

            elif 'START TIME' == first_of_line:
                start_time = line[30:].strip()

        # try:
        #     data = pd.read_table(
        #         cnv_file,
        #         skiprows=m,
        #         sep='\s+',
        #         header=None,
        #         encoding_errors='ignore',
        #     )
        #
        #     if len(data.columns) != no_channels:
        #         data = read_table_vertically(cnv_file, fid, m)
        # except:
        #     data = read_table_vertically(cnv_file, fid, m)

        data = read_table_vertically(cnv_file, fid, m)

        depth_list = []
        press_list = []
        temp_list = []
        sal_list = []

        if depthvar is not None:
            depth_list = list(map(float, data.iloc[:, depthvar].values))
        if pressvar is not None:
            press_list = list(map(float, data.iloc[:, pressvar].values))
        if tempvar is not None:
            temp_list = list(map(float, data.iloc[:, tempvar].values))
        if salvar is not None:
            sal_list = list(map(float, data.iloc[:, salvar].values))

    ctd = dict(
        filename=cnv_file,
        depth=depth_list,
        press=press_list,
        temp=temp_list,
        psal=sal_list,
        mission=mission,
        agency=agency,
        platform=platform,
        type=type_,
        station=station,
        lon=lon,
        lat=lat,
        start_time=start_time,
    )

    return ctd
