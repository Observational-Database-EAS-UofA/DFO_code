from bot_rd_DFO import bot_rd_DFO
from ctd_rd_DFO import ctd_rd_DFO
from che_rd_DFO import che_rd_DFO
from read_DFO_Water_Props_files import *
import sys


def runBOTFiles(data_path=None, save_path=None):
    # bot_rd_DFO("../original_data/1952-001-0059.bot")
    save_bot_files(data_path, save_path)


def runCTDFiles(data_path=None, save_path=None):
    ctd_ctd = ctd_rd_DFO("../original_data/2007-020-0007.ctd")
    print(ctd_ctd)
    # save_bot_files(data_path, save_path)


def runCHEFiles(data_path=None, save_path=None):
    print(che_rd_DFO(data_path))
    # save_bot_files(data_path, save_path)


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
    runBOTFiles(data_path, save_path)


if __name__ == "__main__":
    # main()
    # runCHEFiles("../original_data", "ncfiles")
    runCHEFiles("../original_data/1997-021-0062.che")
