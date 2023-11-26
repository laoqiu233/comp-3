from . import compile_pipeline


if __name__ == "__main__":
    with open("examples/hello_user_name.lisq", encoding="utf-8") as file:
        with open("output.json", "w", encoding="utf-8") as output:
            compile_pipeline(file, output)
