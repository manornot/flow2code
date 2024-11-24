import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import networkx as nx
from src.graph.graph_processor import GraphProcessor
from src.generator.code_generator import CodeGenerator

def test_code_generation():
    graph = nx.DiGraph()
    graph.add_node("n1", type="terminator", label="START")
    graph.add_node("n2", type="input_output", label="x:int")
    graph.add_edge("n1", "n2")

    processor = GraphProcessor(graph)
    processor.parse_graph()

    generator = CodeGenerator(processor)
    code = generator.generate_code()

    assert "x = input()" in code

