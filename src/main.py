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
    get_all_data(data_path, save_path)


if __name__ == "__main__":
    # main()

    # run all files
    get_all_data("../original_data", "ncfiles_raw", ".bot")
    # get_all_data("../original_data", "ncfiles_raw", ".ctd")
    get_all_data("../original_data", "ncfiles_raw", ".che")

    # run individual files
    # print(read_DFO("../original_data/2013-006-0006.che"))
