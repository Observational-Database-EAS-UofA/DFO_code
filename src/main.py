from read_DFO_Water_Props_files import *
import sys


def main():
    if len(sys.argv) != 3:
        print("Usage: python program.py <data_path> <save_path>")
        sys.exit(1)

    data_path = sys.argv[1]
    save_path = sys.argv[2]

    if not os.path.isdir(data_path):
        print(f"Error: '{data_path}' is not a valid directory.")
        sys.exit(1)

    if not os.path.isdir(save_path):
        print(f"Error: '{save_path}' is not a valid directory.")
        sys.exit(1)
    get_raw_data(data_path, save_path)


if __name__ == "__main__":
    # main()

    original_data_path = '/home/novaisc/workspace/obs_database/AW_CAA/CTD_DATA/DFO_IOS_2022/original_data'
    save_path = '/home/novaisc/workspace/obs_database/AW_CAA/CTD_DATA/DFO_IOS_2022/ncfiles_raw'

    for file_type in ['.bot', '.che', '.ctd']:
        get_raw_data(original_data_path, save_path, file_type=file_type)
