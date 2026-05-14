import sys

from minnelove_emu.cli import main


if __name__ == "__main__":
    main(["make-linux-script", *sys.argv[1:]])
