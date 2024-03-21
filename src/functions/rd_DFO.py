from src.functions.reader import read_table_vertically
from datetime import datetime


def read_DFO(cnv_file, FMT='IR'):
    header_str = ''
    project = None
    platform = None
    scientist = None
    instrument_type = None
    station_no = None
    lat = None
    lon = None
    number_of_records = None
    water_depth = None
    shallowest_depth = None
    deepest_depth = None
    datestr = None
    timezone = None
    timestamp = None

    no_channels = None
    depthvar = None
    pressvar = None
    tempvar = None
    salvar = None

    # Read the header.
    with open(cnv_file, 'r', errors="ignore") as fid:
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

            elif 'PLATFORM' == first_of_line:
                platform = line.split(':')[1].strip()
            elif 'PROJECT' == first_of_line:
                project = line.split(':')[1].strip()
            elif 'SCIENTIST' == first_of_line:
                scientist = line.split(':')[1].strip()
            elif 'TYPE' == first_of_line:
                instrument_type = line.split(':')[1].strip()
            elif 'STATION' == first_of_line:
                station_no = line.split(':')[1].strip()
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
                lon_direction = lon_str[2]
                if lon_direction == 'W':
                    lon = -1 * (lon_deg + lon_min / 60)
                elif lon_direction == 'E':
                    lon = lon_deg + lon_min / 60
                else:
                    print("deu merda")
                lon = float(f'{lon: .4f}')
            elif 'START TIME' == first_of_line:
                first_colon = line.find(':')
                full_date = line[first_colon + 1:].strip()
                timezone = full_date.split()[0]
                datestr = full_date.replace(timezone, '').strip()
                datestr = datetime.strptime(datestr, "%Y/%m/%d %H:%M:%S.%f")
                timestamp = datestr.timestamp()
                datestr = datetime.strftime(datestr, "%Y/%m/%d %H:%M:%S")
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

    if len(depth_list) > 0:
        shallowest_depth = depth_list[0]
        i = 1
        while not shallowest_depth > 0 and len(depth_list) > 1:
            shallowest_depth = depth_list[i]
            i += 1
        deepest_depth = depth_list[-1]

    ctd = dict(
        cruise_name=project,
        chief_scientist=scientist,
        platform=platform,
        instrument_type=instrument_type,
        orig_filename=cnv_file,
        orig_header=header_str,
        station_no=station_no,
        datestr=datestr,
        timezone=timezone,
        timestamp=timestamp,
        lat=lat,
        lon=lon,
        num_records=number_of_records,
        shallowest_depth=shallowest_depth,
        deepest_depth=deepest_depth,
        bottom_depth=water_depth,
        depth=depth_list,
        press=press_list,
        temp=temp_list,
        psal=sal_list,
    )

    return ctd
