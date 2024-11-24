import networkx as nx

# Validation rules for each block type
BLOCK_RULES = {
    "input_output": {"inputs": 1, "outputs": 1},
    "process": {"inputs": 1, "outputs": 1},
    "decision": {"inputs": 1, "outputs": 2},  # Yes/No branches
    "loop": {"inputs": 2, "outputs": 2},      # Entry/Body and Termination
    "terminator": {"inputs": "any", "outputs": "any"},  # START/END blocks
    "connector": {"inputs": "any", "outputs": 1},       # Merging flows
}


def validate_graph(graph, nodes):
    """
    Validates the graph structure, ensuring all nodes and edges comply with flowchart rules.
    Returns a list of validation errors.
    """
    errors = []

    # Validate nodes
    errors.extend(validate_nodes(graph, nodes))

    # Validate edges
    errors.extend(validate_edges(graph, nodes))

    # Validate loops
    errors.extend(validate_loops(graph, nodes))

    # Check for disconnected components
    if not nx.is_weakly_connected(graph):
        errors.append("The graph has disconnected components. Ensure all blocks are connected.")

    return errors


def validate_nodes(graph, nodes):
    """
    Validates individual nodes for compliance with block type rules.
    """
    errors = []

    for node_id, data in nodes.items():
        node_type = data.get("type", "unknown")
        rules = BLOCK_RULES.get(node_type, None)

        if not rules:
            errors.append(f"Unknown node type: {node_type} (Node ID: {node_id})")
            continue

        # Validate input and output connections
        in_degree = graph.in_degree(node_id)
        out_degree = graph.out_degree(node_id)

        if rules["inputs"] != "any" and in_degree != rules["inputs"]:
            errors.append(f"Node {node_id} ({node_type}) has invalid inputs: expected {rules['inputs']}, found {in_degree}")

        if rules["outputs"] != "any" and out_degree != rules["outputs"]:
            errors.append(f"Node {node_id} ({node_type}) has invalid outputs: expected {rules['outputs']}, found {out_degree}")

    return errors


def validate_edges(graph, nodes):
    """
    Validates edges, ensuring they have proper labels and connect valid node types.
    """
    errors = []

    for source, target, edge_data in graph.edges(data=True):
        source_type = nodes[source]["type"]
        target_type = nodes[target]["type"]

        # Validate edge labels for decision nodes
        if source_type == "decision":
            label = edge_data.get("label", "").lower()
            if label not in {"yes", "no"}:
                errors.append(f"Decision node {source} has an edge without a valid label ('Yes' or 'No').")

        # Validate edge connections (e.g., no direct connection to connectors without reason)
        if target_type == "connector" and source_type not in {"decision", "loop"}:
            errors.append(f"Edge from {source} ({source_type}) to {target} ({target_type}) is invalid.")

    return errors


def detect_loops(graph, nodes):
    """
    Detects loops in the graph based on cycles and decision blocks.
    Marks nodes and edges as part of loops if detected.
    """
    loops = []  # List to store detected loops
    cycles = list(nx.simple_cycles(graph))  # Detect cycles in the graph

    for cycle in cycles:
        if len(cycle) < 2:
            continue  # Skip trivial cycles (e.g., self-loops)

        # Check if the entry point of the cycle is a decision block
        entry_node = cycle[0]
        if nodes[entry_node]["type"] == "decision":
            loops.append(cycle)

            # Mark all nodes in the cycle as part of a loop
            for node in cycle:
                nodes[node]["is_loop"] = True

            # Mark edges in the cycle as part of the loop
            for i in range(len(cycle)):
                source = cycle[i]
                target = cycle[(i + 1) % len(cycle)]  # Wrap around for the last edge
                graph.edges[source, target]["is_loop"] = True

    return loops


def validate_loops(graph, nodes):
    """
    Validates loops in the graph, including hexagonal blocks and decision-based loops.
    """
    errors = []

    # Detect and mark loops
    loops = detect_loops(graph, nodes)

    for loop in loops:
        entry_node = loop[0]

        # Hexagonal loop validation
        if nodes[entry_node]["type"] == "loop":
            continue  # Explicit loop blocks are valid by default

        # Decision-based loop validation
        if nodes[entry_node]["type"] == "decision":
            successors = list(graph.successors(entry_node))
            returning_edges = [
                (entry_node, succ) for succ in successors
                if graph.edges[entry_node, succ].get("is_loop", False)
            ]
            if not returning_edges:
                errors.append(f"Loop starting at decision node {entry_node} has no valid return edge.")
        else:
            errors.append(f"Loop detected but entry node {entry_node} is not a valid loop or decision block.")

    return errors
