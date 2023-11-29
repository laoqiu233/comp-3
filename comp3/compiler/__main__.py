import sys
from pathlib import Path

from . import compile_pipeline


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Invalid arguments. Usage: compiler <input_file> <output_file>")

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(sys.argv[1], encoding="utf-8") as file:
        with open(sys.argv[2], "w", encoding="utf-8") as output:
            compile_pipeline(file, output)
