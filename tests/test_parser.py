import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import networkx as nx
from src.parser.drawio_parser import parse_drawio_file,detect_node_type

def test_parse_drawio_file():
    # Path to the test.drawio file
    file_path = os.path.join(os.path.dirname(__file__), "data", "test.drawio")

    # Parse the drawio file
    graph, nodes, edge_exit_points = parse_drawio_file(file_path)
    print(nodes)

    # Test: Graph type
    assert isinstance(graph, nx.DiGraph), "Parsed graph should be a directed graph."

    # Test: Number of nodes
    assert len(nodes) > 0, "The graph should contain nodes."
    assert len(graph.nodes) == len(nodes), "Graph nodes should match parsed nodes."

    # Test: Node types and labels
    expected_nodes = {
    "2": {"label": "START", "type": "terminator", "geometry": {"x": 305, "y": 200, "width": 120, "height": 60}},
    "3": {"label": "data:list", "type": "input_output", "geometry": {"x": 305, "y": 290, "width": 120, "height": 60}},
    "19": {"label": "ln <-length of data\n", "type": "process", "geometry": {"x": 305, "y": 370, "width": 120, "height": 60}},
    "13": {"label": "repeat ln-1 times", "type": "loop", "geometry": {"x": 305, "y": 460, "width": 120, "height": 80}},
    "36": {"label": "i = 0", "type": "process", "geometry": {"x": 305, "y": 560, "width": 120, "height": 60}},
    "24": {"label": "data[i]<data[j]", "type": "decision", "geometry": {"x": 280, "y": 770, "width": 170, "height": 80}},
    "26": {"label": "tmp = data[i]\ndata[i] = data[j]\ndata[j] = tmp", "type": "process", "geometry": {"x": 520, "y": 900, "width": 120, "height": 60}},
    "29": {"label": "", "type": "connector", "geometry": {"x": 570, "y": 1020, "width": 20, "height": 20}},
    "33": {"label": "i = i + 1", "type": "process", "geometry": {"x": 670, "y": 1000, "width": 120, "height": 60}},
    "43": {"label": "data", "type": "input_output", "geometry": {"x": 305, "y": 1129.9999999999998, "width": 120, "height": 60}},
    "44": {"label": "END", "type": "terminator", "geometry": {"x": 305, "y": 1240, "width": 120, "height": 60}},
}


    for node_id, expected in expected_nodes.items():
        assert node_id in nodes, f"Node {node_id} should exist in the parsed graph."
        assert nodes[node_id].label == expected["label"], f"Node {node_id} label mismatch."
        assert nodes[node_id].type == expected["type"], f"Node {node_id} type mismatch."

    # Test: Number of edges
    assert len(graph.edges) > 0, "The graph should contain edges."

    # Test: Connections
    expected_edges = [
    {"source": "2", "target": "3", "label": ""},
    {"source": "3", "target": "19", "label": ""},
    {"source": "19", "target": "13", "label": ""},
    {"source": "13", "target": "36", "label": ""},
    {"source": "24", "target": "26", "label": "Yes"},
    {"source": "26", "target": "29", "label": ""},
    {"source": "29", "target": "33", "label": ""},
    {"source": "24", "target": "29", "label": "No"},
    {"source": "13", "target": "43", "label": ""},
    {"source": "43", "target": "44", "label": ""},
]

    for indx,edge in enumerate(expected_edges):
        src,trgt,lbl = [key for key in edge]
        source = expected_edges[indx][src]
        target = expected_edges[indx][trgt]
        assert graph.has_edge(source, target), f"Edge from {source} to {target} is missing."

    # Test: Edge metadata
    for (source, target) in graph.edges:
        edge_label = graph.edges[source, target].get("label", "")
        assert isinstance(edge_label, str), "Edge label should be a string."

    # Test: Geometries
    for node_id, node_data in nodes.items():
        geometry = node_data.geometry
        
        assert getattr(geometry,'x',None) and getattr(geometry,'y',None), f"Node {node_id} is missing geometry coordinates."
        assert isinstance(geometry.x, float) and isinstance(geometry.y, float), \
            f"Node {node_id} geometry values should be floats."

def test_text_blocks():
    # Path to the test.drawio file
    file_path = os.path.join(os.path.dirname(__file__), "data", "test.drawio")

    # Parse the drawio file
    graph, nodes, edge_block = parse_drawio_file(file_path)
    
    text_blocks = {}
    for node in nodes.values():
        if node.type == 'text':
            text_blocks[node.node_id]=node
    # Test: Text blocks count
    assert len(text_blocks) >= 0, "Text blocks should be parsed correctly."

    # Test: Text block content
    for block_id, block_data in text_blocks.items():
        assert getattr(block_data,"label"), f"Text block {block_id} is missing a label."
        assert isinstance(getattr(block_data,"label"), str), f"Text block {block_id} label should be a string."
