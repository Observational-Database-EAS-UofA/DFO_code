from src.shared.reader import read_table_vertically


def read_DFO(cnv_file, FMT='IR'):
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
        print(cnv_file)
        line = '*START*'
        already_entered = False
        while '*END OF HEADER' not in line:
            line = fid.readline()
            first_of_line = line.split(":")[0].strip()
            header_str += line
            if 'NUMBER OF CHANNELS' == first_of_line:
                no_channels = int(line.split(':')[1])

            elif '$TABLE: CHANNELS' == line.strip() and no_channels is not None and already_entered is False:
                already_entered = True
                line = fid.readline()
                line = fid.readline()
                for mm in range(no_channels):
                    line = fid.readline().strip().split()
                    if ":" in line[1]:
                        line = line[1].split(":")[0]

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

            elif 'LONGITUDE' == first_of_line:
                lon_str = line.split(':')[1].strip().split()
                lon_deg = float(lon_str[0])
                lon_min = float(lon_str[1])
                lon = -1 * (lon_deg + lon_min / 60)

            elif 'START TIME' == first_of_line:
                start_time = line[30:].strip()

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
