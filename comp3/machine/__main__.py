import logging
import sys

from comp3.machine import main


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        flags = set(filter(lambda x: x.startswith('--'), sys.argv))
        statistics = "--show-statistics" in flags
        logs = "--logs" in sys.argv[3:]

        input_stream = ""
        for arg in sys.argv[2:]:
            if arg in flags: continue
            input_stream = arg
            break
        
        if logs:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
            
        main(sys.argv[1], input_stream, statistics)
    else:
        print("Invalid arguments. Usage: machine <source program> [<input string>] [--show-statistics, --logs]")
