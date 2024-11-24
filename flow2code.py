
import subprocess
import sys
import importlib
from pathlib import Path

# Function to install module via pip
def install_and_import(package):
    try:
        importlib.import_module(package)
    except ImportError:
        print(f"{package} not found, installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    finally:
        globals()[package] = importlib.import_module(package)


with open('requirements.txt') as f:
    packages = f.read().split()

for package in packages:
    install_and_import(package)


import os
from src.parser.drawio_parser import parse_drawio_file
from src.generator.graph2block import G2BConverter
from src.utils.matching import map_labels_to_edges
from src.generator.CodeGenerationManager import CodeGenerationManager


def convert_to_code(nested_list):
    code = '''
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout


def custom_debugger():
    session = PromptSession()
    with patch_stdout():
        print(globals())
        session.prompt("Debugging... Press Enter to continue.")
    '''
    code_lines = []

    for item in nested_list:
        indent_level = item[1]
        code_content = item[2][0].split('\n')

        for line in code_content:
            code_lines.append('    ' * indent_level + line)
            code_lines.append('    ' * (indent_level+1) + 'custom_debugger()')

    return '\n'.join([code,'\n'.join(code_lines)])

def find_starting_node(graph):
    # Manual in-degree calculation
    in_degree_count = {node: 0 for node in graph.nodes}

    # Iterate over the edges to calculate in-degrees
    for from_node, to_node in graph.edges:
        in_degree_count[to_node] += 1

    # Find all nodes with no incoming edges (in-degree 0)
    starting_nodes = [node for node, in_degree in in_degree_count.items() if in_degree == 0]

    # Refine to select a unique starting node
    if not starting_nodes:
        raise ValueError("No starting node found with in-degree 0")

    # Choose the node with the smallest identifier
    if len(starting_nodes) >= 1:
        starting_nodes = starting_nodes[0]
    return starting_nodes


pth_to_file = input("enter path to drawio file")
pth_to_file = pth_to_file.replace('\\\\',"\\").replace('"','').replace("'",'').replace(' ','')
file_path = Path(os.path.abspath(pth_to_file))
graph = parse_drawio_file(file_path)
map_labels_to_edges(graph)
converter = G2BConverter(graph)
starting_nodes = find_starting_node(graph)
blocks = converter.graph_to_blocks(starting_nodes)

cgm = CodeGenerationManager()
for block in blocks:
    while isinstance(block, list):
        block = block[0]
        if block is None:
            break
    cgm.add_block(block)
code_prep = cgm.process_blocks()
print(convert_to_code(code_prep))