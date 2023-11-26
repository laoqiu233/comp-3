from comp3.compiler import compile_pipeline

if __name__ == "__main__":
    with open("examples/hello_user_name.lisq") as file:
        with open("output.json", "w") as output:
            compile_pipeline(file, output)
