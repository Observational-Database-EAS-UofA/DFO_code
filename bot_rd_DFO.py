import numpy as np
import pandas as pd
import datetime


def bot_rd_DFO(cnv_file, FMT='IR'):
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
    no_channels = None
    depthvar = None
    pressvar = None
    tempvar = None
    salvar = None

    with open(cnv_file, 'r', errors="ignore") as fid:
        line = '*START*'
        while '*END OF HEADER' not in line:
            line = fid.readline()
            first_of_line = line.split(":")[0].strip()
            header_str += line
            if 'NUMBER OF CHANNELS' == first_of_line:
                no_channels = int(line.split(':')[1])

            elif '$TABLE: CHANNELS' == line.strip():
                line = fid.readline()
                line = fid.readline()
                for mm in range(no_channels):
                    line = fid.readline().strip()
                    if 'Depth' in line:
                        depthvar = mm
                    elif 'Pressure' in line:
                        pressvar = mm
                    elif 'Temperature' in line:
                        tempvar = mm
                    elif 'Salinity' in line:
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
                # lat = float('%.4f' % lat)

            elif 'LONGITUDE' == first_of_line:
                lon_str = line.split(':')[1].strip().split()
                lon_deg = float(lon_str[0])
                lon_min = float(lon_str[1])
                lon = -1 * (lon_deg + lon_min / 60)
                # lon = float('%.4f' % lon)

            elif 'START TIME' == first_of_line:
                start_time = line[30:].strip()

        # Done reading header. Now read the data.
        data = []
        for line in fid:
            data.append(list(map(float, line.split())))

        depth_list = []
        press_list = []
        temp_list = []
        sal_list = []

        for row in data:
            if depthvar is not None:
                depth_list.append(row[depthvar])
            if pressvar is not None:
                press_list.append(row[pressvar])
            if tempvar is not None:
                temp_list.append(row[tempvar])
            if salvar is not None:
                sal_list.append(row[salvar])

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
