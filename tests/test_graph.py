# tests/test_graph.py


import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import networkx as nx
from src.graph.graph import find_entry_nodes, compute_immediate_dominators
from src.graph.loop_analysis import analyze_loops, group_loops_by_causal_node

def test_find_entry_nodes():
    # Create a mock graph
    graph = nx.DiGraph()
    graph.add_node(1)
    graph.add_node(2)
    graph.add_edge(1, 2)

    # Find entry nodes
    entry_nodes = find_entry_nodes(graph)
    assert len(entry_nodes) == 1, "Expected exactly one entry node."
    assert entry_nodes[0] == 1, "Entry node is incorrect."

def test_compute_immediate_dominators():
    # Create a mock graph
    graph = nx.DiGraph()
    graph.add_edges_from([(1, 2), (2, 3), (3, 4), (2, 5)])

    # Compute dominators
    dominators = compute_immediate_dominators(graph, [1])
    assert 1 in dominators, "Entry node should have a dominator tree."
    assert dominators[1][3] == 2, "Dominator tree is incorrect."

from src.graph.loop_analysis import analyze_loops
import networkx as nx

def test_analyze_loops():
    # Create a mock graph with a loop
    graph = nx.DiGraph()
    graph.add_edges_from([(1, 2), (2, 3), (3, 1)])  # Loop: 1 → 2 → 3 → 1

    # Mock node metadata
    nodes = {
        1: {"type": "process", "label": "x = x + 1"},
        2: {"type": "process", "label": "y = x - 1"},
        3: {"type": "decision", "label": "x > 10"},  # Node 3 must match desired_types
    }

    # Generate dominator tree dynamically
    entry_node = 1
    dominator_tree = {entry_node: nx.immediate_dominators(graph, entry_node)}

    # Analyze loops
    loops_by_node = analyze_loops(graph, dominator_tree, nodes, {"decision"})

    # Assertions
    assert len(loops_by_node) > 0, "Expected loops to be detected."
    assert 3 in loops_by_node, "Node 3 should be identified as causing a loop."
    assert len(loops_by_node[3]) > 0, "Node 3 should have at least one loop associated."
    assert loops_by_node[3][0]["back_edge"] == (3, 1), "Expected back edge (3, 1)."
