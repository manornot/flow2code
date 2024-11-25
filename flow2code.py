import subprocess
import sys
import importlib
from pathlib import Path
import os


def create_virtual_environment(venv_path):
    # Check if the virtual environment already exists
    if not venv_path.exists():
        print("Creating virtual environment...")
        subprocess.check_call([sys.executable, "-m", "venv", str(venv_path)])
        return
    else:
        print("Virtual environment already exists.")


def install_and_import(package, venv_python):
    try:
        importlib.import_module(package)
    except ImportError:
        print(f"{package} not found, installing...")
        subprocess.check_call([venv_python, "-m", "pip", "install", package])
    finally:
        globals()[package] = importlib.import_module(package)


def select_file(sender, app_data):
    # File path for the selected file
    file_path = app_data["file_path_name"]
    file_path = os.path.abspath(file_path)
    # Update label text to show the selected file path
    dpg.set_value("file_path_label", f"Selected file: {file_path}")
    # Proceed with your logic using 'file_path'
    process_file(file_path)


def show_file_dialog(sender, app_data):
    dpg.show_item("file_dialog_id")


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
            if not any([kwrd in line for kwrd in ['pass', 'if', 'else', 'with', 'while', 'for', 'finally']]):
                code_lines.append('    ' * indent_level + 'custom_debugger()')
            code_lines.append('    ' * indent_level + line)
    return '\n'.join([code, '\n'.join(code_lines)])


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


def process_file(file_path):
    # Convert file path to pathlib.Path
    file_path = Path(file_path)
    # Ensure file path is absolute and expand user path if any
    file_path = file_path.expanduser().resolve()
    graph = parse_drawio_file(file_path)
    map_labels_to_edges(graph)
    converter = G2BConverter(graph)
    starting_node = find_starting_node(graph)
    blocks = converter.graph_to_blocks(starting_node)
    cgm = CodeGenerationManager()
    for block in blocks:
        while isinstance(block, list):
            block = block[0]
            if block is None:
                break
        cgm.add_block(block)
    code_prep = cgm.process_blocks()
    print(convert_to_code(code_prep))


if __name__ == "__main__":
    # Define the path for the virtual environment
    project_dir = Path(__file__).parent
    venv_dir = project_dir / 'venv'
    # Name of the Python interpreter in the virtual environment
    venv_python = venv_dir / 'Scripts' / 'python' if os.name == 'nt' else venv_dir / 'bin' / 'python'
    # Create the virtual environment if it doesn't exist
    create_virtual_environment(venv_dir)
    # Determine if we're running inside the virtual environment by checking the 'VIRTUAL_ENV' environment variable
    if 'VIRTUAL_ENV' not in os.environ:
        if 'VIRTUAL_ENV_ACTIVATED' not in os.environ:
            print("Re-running script within virtual environment...")
            # Set environment variable to avoid infinite loop
            env = os.environ.copy()
            env['VIRTUAL_ENV_ACTIVATED'] = '1'
            subprocess.check_call([str(venv_python), __file__], env=env)
            sys.exit(0)

    # Continue with the existing code logic
    with open('requirements.txt') as f:
        packages = f.read().split()

    for package in packages:
        install_and_import(package, str(venv_python))

    # Import the required modules after they are installed
    from src.parser.drawio_parser import parse_drawio_file
    from src.generator.graph2block import G2BConverter
    from src.utils.matching import map_labels_to_edges
    from src.generator.CodeGenerationManager import CodeGenerationManager
    import dearpygui.dearpygui as dpg

    # Create context for Dear PyGui
    dpg.create_context()
    # Main window with explicit ID
    with dpg.window(label="File Selector", id="main_window", width=500, height=500):
        dpg.add_button(label="Select drawio file", callback=show_file_dialog)
        dpg.add_text("", tag="file_path_label")
    # File dialog
    with dpg.file_dialog(directory_selector=False, show=False, callback=select_file,
                         id="file_dialog_id", width=450, height=450,
                         file_count=1, modal=True, tag="file_dialog_tag"):
        dpg.add_file_extension(".drawio", color=(150, 255, 150, 255))
        dpg.add_file_extension(".*")
    # Create and show the viewport
    dpg.create_viewport(title="Select drawio file", width=500, height=500)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("main_window", True)
    dpg.start_dearpygui()
    # Clean up context
    dpg.destroy_context()