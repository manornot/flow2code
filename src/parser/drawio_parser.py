# src/parser.py

import xml.etree.ElementTree as ET
from typing import Dict, Tuple
import networkx as nx
from pathlib import Path

def parse_drawio_file(file_path: Path) -> nx.DiGraph:
    """
    Parses the draw.io file and constructs a graph.

    Returns:
        graph (nx.DiGraph): The constructed graph with nodes and edges.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    graph = nx.DiGraph()

    # Extract cells from the XML
    cells = root.findall(".//mxCell")

    # Maps cell IDs to their data
    cell_data = {}

    for cell in cells:
        cell_id = cell.get('id')
        if not cell_id:
            continue

        # Get node or edge attributes
        value = cell.get('value', '').strip()
        style = cell.get('style', '')
        vertex = cell.get('vertex') == '1'
        edge = cell.get('edge') == '1'
        geometry_elem = cell.find('mxGeometry')
        if geometry_elem is not None:
            geometry = {
                'x': float(geometry_elem.get('x', '0')),
                'y': float(geometry_elem.get('y', '0')),
                'width': float(geometry_elem.get('width', '0')),
                'height': float(geometry_elem.get('height', '0')),
        }
        

        if vertex:
            node_type = detect_node_type(cell)
            if node_type == "input_output":
                if ':' in value:
                    node_type = "input"
                else:
                    node_type = "output"
            graph.add_node(cell_id, type=node_type, label=value, geometry=geometry)
        elif edge:
            source = cell.get('source')
            target = cell.get('target')
            if source and target:
                
                
                graph.add_edge(source, target,style=style)

    return graph




def detect_node_type(cell) -> str:
    """
    Determines the node type based on the style string.

    Returns:
        node_type (str): The type of the node.
    """
    style = cell.get('style', '')
    value = cell.get('value', '').strip()
    if "shape=parallelogram" in style:
        return "input_output"
    elif "rhombus" in style:
        return "decision"
    elif "shape=hexagon" in style:
        if 'repeat' in value.lower():
            return "repeat_loop"
        elif 'for' in value.lower():
            return "for_each_loop"
        else:
            raise ValueError('in Hex block the only "repeat <x> times" or "for each <elem> in <some_array>" should appear')
            
    elif "rounded=1" in style:
        return "terminator"
    elif "ellipse" in style or "shape=ellipse" in style:
        return "connector"
    elif "text;" in style or ("strokeColor=none" in style and "fillColor=none" in style):
        return "text"
    return "process"  # Default type

if __name__ == "__main__":
    # Example usage
    file_path = Path(r'C:\Users\orman\Documents\MimicHub\Pygorithm\tests\data\test.drawio')
    graph = parse_drawio_file(file_path)
    print(graph.nodes(data=True))
    print(graph.edges(data=True))