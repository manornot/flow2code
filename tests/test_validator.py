import os
import pytest
from src.parser.drawio_parser import parse_drawio_file
from src.parser.validator import validate_graph

def test_bubble_sort_parsing_and_validation():
    file_path = os.path.join(os.path.dirname(__file__), "data", r"test.drawio")

    # Parse the Draw.io file
    graph, nodes, _, _ = parse_drawio_file(file_path)

    # Validate the graph
    errors = validate_graph(graph, nodes)

    # Verify no validation errors
    assert not errors, f"Validation failed for Bubble Sort graph: {errors}"

    # Verify loop detection
    detected_loops = [node_id for node_id, data in nodes.items() if data.get("is_loop", False)]
    assert len(detected_loops) >= 2, "Expected at least two loops: hexagonal and decision-based."
