import sys

from comp3.machine import main


if __name__ == "__main__":
    if len(sys.argv) != 3 or (len(sys.argv) == 4 and sys.argv[3] != 'show-statistics'):
        print("Invalid arguments. Usage: machine <source program> <input string> [show-statistics]")

    statistics = len(sys.argv) == 4 and sys.argv[3] == 'show-statistics'

    main(sys.argv[1], sys.argv[2], statistics)
