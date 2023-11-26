import re

def process_includes(content: str):
    matches = re.findall(r'#include (.+)\n', content)

    for filename in set(matches):
        with open(filename) as file:
            included_content = file.read()
            content = content.replace(f'#include {filename}\n', included_content)

    return content