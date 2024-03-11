import numpy as np

from src.shared.reader import read_table_vertically
from datetime import datetime


def read_DFO(cnv_file, FMT='IR'):
    header_str = ''
    mission = None
    agency = None
    platform = None
    type_ = None
    station = None
    lat = None
    lon = None
    number_of_records = None
    water_depth = None
    start_time = None
    serial_time = None

    no_channels = None
    depthvar = None
    pressvar = None
    tempvar = None
    salvar = None

    # Read the header.
    with open(cnv_file, 'r', errors="ignore") as fid:
        print(cnv_file)
        line = '*START*'
        already_entered_table_channels = False
        while '*END OF HEADER' not in line:
            header_str += str(line)
            line = fid.readline()
            first_of_line = line.split(":")[0].strip()
            if 'NUMBER OF CHANNELS' == first_of_line:
                no_channels = int(line.split(':')[1])

            elif '$TABLE: CHANNELS' == line.strip() and no_channels is not None and already_entered_table_channels is False:
                already_got_salinity = False
                already_entered_table_channels = True
                line = fid.readline()
                line = fid.readline()
                for mm in range(no_channels):
                    line = fid.readline().strip().split()
                    old_line = line
                    if ":" in line[1]:
                        line = line[1].split(":")[0]
                    if 'Depth' in line:
                        depthvar = mm
                    elif 'Pressure' in line:
                        pressvar = mm
                    elif 'Temperature' in line:
                        tempvar = mm
                    # prefer the 'Salinity' only
                    elif old_line[1].startswith('Salinity') and old_line[1] != 'Salinity:Bottle':
                        salvar = mm
                        already_got_salinity = True
                    elif 'Salinity' in line and already_got_salinity is False:
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
                lat = float(f'{lat: .4f}')

            elif 'LONGITUDE' == first_of_line:
                lon_str = line.split(':')[1].strip().split()
                lon_deg = float(lon_str[0])
                lon_min = float(lon_str[1])
                lon = -1 * (lon_deg + lon_min / 60)
                lat = float(f'{lon: .4f}')

            elif 'START TIME' == first_of_line:
                datestr = line[30:].strip()
                # datestr = datetime.strptime(datestr, "%Y/%m/%d %H:%M:%S.%f")
                serial_time = datetime.strptime(datestr, "%Y/%m/%d %H:%M:%S.%f").timestamp()

            elif 'NUMBER OF RECORDS' == first_of_line:
                number_of_records = line.split(':')[1].strip()

            elif 'WATER DEPTH' == first_of_line:
                water_depth = line.split(':')[1].strip()

        data = read_table_vertically(cnv_file, fid)

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
        header=header_str,
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
        number_of_records=number_of_records,
        water_depth=water_depth,
        datestr=datestr,
        serial_time=serial_time,
    )

    return ctd
