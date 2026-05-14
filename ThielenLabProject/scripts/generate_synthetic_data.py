import sys

from minnelove_emu.cli import main


if __name__ == "__main__":
    main(["generate-demo", *sys.argv[1:]])
