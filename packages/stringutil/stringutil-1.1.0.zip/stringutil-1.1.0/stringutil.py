"""a collection of basic string utility methods, mostly created for learning python...sorry..."""

def lines(file):
    for line in file: yield line
    yield '\n'

def blocks(file):
    block = []
    for line in lines(file):
        if line.strip():
            block.append(line)
        elif block:
            yield ''.join(block).strip()
            block = [];


def print_recursive(a_list, indent=False, indent_level=0):
    """Recursively prints a list structure"""

    for item in a_list:
        if isinstance(item, list):
            print_recursive(item, indent_level+1)
        else:
            for indent in range(indent_level):
                print("\t", end='')
            print(item)
