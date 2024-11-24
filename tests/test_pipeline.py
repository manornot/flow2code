# tests/test_pipeline.py

import os
from src.parser.drawio_parser import parse_drawio_file
from src.graph.graph import find_entry_nodes, compute_immediate_dominators
from src.generator.code_generator import generate_code, validate_generated_code

def test_pipeline():
    # Sample .drawio file path
    test_file = os.path.abspath(r"C:\Users\orman\Documents\MimicHub\Pygorithm\tests\data\test.drawio")

    # Parse the file
    graph, nodes, edge_exit_points = parse_drawio_file(test_file)
    assert len(graph.nodes) > 0, "Parsing failed: Graph has no nodes."

    # Analyze the graph
    entry_nodes = find_entry_nodes(graph)
    dominator_trees = compute_immediate_dominators(graph, entry_nodes)

    # Mock loop analysis
    loops_by_node = {}

    # Generate code
    code = generate_code(graph, nodes, loops_by_node)
    assert len(code.strip()) > 0, "Generated code is empty."

    # Validate the code
    is_valid, error = validate_generated_code(code)
    print(code)
    assert is_valid, f"Generated code is invalid: {error}"
