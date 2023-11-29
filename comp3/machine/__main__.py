import logging
import sys

from comp3.machine import main


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        flags = set(filter(lambda x: x.startswith("--"), sys.argv))
        statistics = "--show-statistics" in flags
        logs = "--logs" in sys.argv[3:]

        not_flags = list(filter(lambda x: x not in flags, sys.argv[2:]))
        input_stream = "" if len(not_flags) == 0 else not_flags[0]

        if logs:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

        main(sys.argv[1], input_stream, statistics)
    else:
        print(
            "Invalid arguments. Usage: machine <source program> [<input string>]"
            " [--show-statistics, --logs]"
        )
