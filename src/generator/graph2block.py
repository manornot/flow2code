import networkx as nx
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from typing import List, Set
from src.generator.blockModel import Block,Input, Output, IfStatement, WhileLoop, RepeatLoop, ForEachLoop
from src.utils.matching import map_labels_to_edges
from src.parser.drawio_parser import parse_drawio_file

class G2BConverter:
    block_map = {
            'process': Block,
            'input':Input,
            'output':Output,
            'while_loop': WhileLoop,
            'repeat_loop': RepeatLoop,
            'for_each_loop': ForEachLoop,
            'decision': IfStatement,
            'terminator': None,  # Start/End nodes, not converted to blocks
            'connector': None,   # Connectors handle flow but don't create blocks
            'text': None         # Text nodes provide labels for edges but are not blocks
        }
    visited = set()

    def __init__(self, graph:nx.DiGraph):
        self.graph = graph

    def create_block(self,node_id):
        """Create a block instance from a node."""
        node_data = self.graph.nodes[node_id]
        block_type = self.block_map.get(node_data['type'])
        if block_type is None:
            return Block(code='pass')
        label = node_data.get('label', '').replace('&lt;', '<').replace('&gt;', '>').replace('<br>', '\n').replace('&nbsp;', ' ')
        if block_type in (IfStatement,WhileLoop):
            return block_type(block_id=node_id ,condition=label)
        elif block_type == RepeatLoop:
            return block_type(block_id=node_id ,counter=label.replace('repeat ', '').replace('times',''))
        elif block_type == ForEachLoop:
            return block_type(block_id=node_id ,iterator_var=label)
        else:
            return block_type(block_id=node_id ,code=label)

    def process_node(self, node_id, visited) -> [Block]:
        """Recursive helper to process nodes."""
        if node_id in visited:
            return [Block(code='pass')]  # Avoid infinite loops due to cycles
        visited.add(node_id)

        node_data = self.graph.nodes[node_id]
        block = self.create_block(node_id)

        if node_data['type'] in ('while_loop', 'repeat_loop', 'for_each_loop'):
            body_successors = [node_id]

            # Classify successors as loop body or exit
            for successor in self.graph.successors(node_id):
                edge_data = self.graph.get_edge_data(node_id, successor, {})
                role = edge_data.get('role', 'normal')
                if role == 'body':
                    body_successors.append(successor)




            node = body_successors[-1]
            loop_not_closed = True
            while loop_not_closed:
                if len(list(self.graph.successors(node))) == 1:
                    successor = list(self.graph.successors(node))[0]
                    if successor == node_id or successor in body_successors:
                        loop_not_closed = False
                        break
                    body_successors.append(successor)
                    node = body_successors[-1]
                else:
                    for successor, edge_data in self.graph[node].items():
                        role = edge_data.get('role', '').lower()
                        if role in ('exit', 'false branch'):
                            if successor == node_id or successor in body_successors:
                                loop_not_closed = False
                                break
                            body_successors.append(successor)
                            node = body_successors[-1]
                

            nested_block = [self.process_node(successor, visited) for successor in body_successors[1:]]
            if nested_block:
                block.body += flatten(nested_block)

            # Process loop exit successor (blocks outside the loop)


        elif node_data['type'] == 'decision':
            # Handle true and false branches
            for successor, edge_data in self.graph[node_id].items():
                label = edge_data.get('label', '').lower()
                nested_block = self.process_node(successor, visited)
                if label == 'yes' and nested_block:
                    block.true_branch_body += flatten(nested_block)
                elif label == 'no' and nested_block:
                    block.false_branch_body += flatten(nested_block)
        return [block]


    def graph_to_blocks(self, start_node: str) -> List[Block]:
        """
        Recursively convert a NetworkX digraph into nested Block instances.
        """
        node = start_node
        black_box = []
        while len(list(self.graph.successors(node)))>0:
            if len(list(self.graph.successors(node))) == 1:
                black_box.append(list(self.graph.successors(node))[0])
                node = black_box[-1]
            else:
                #go through successor which edge is marked as 'exit' or 'no'
                for successor, edge_data in self.graph[node].items():
                    label = edge_data.get('role', '').lower()
                    if label in ('exit', 'no'):
                        black_box.append(successor)
                        node = black_box[-1]
        return [self.process_node(start_node,set()) for start_node in black_box]


def flatten(nested_list):
    """
    Recursively flattens a nested list of arbitrary depth.

    :param nested_list: A list, potentially containing other lists
    :return: A single flat list with all the values from the nested lists
    """
    flat_list = []

    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten(item))
        else:
            flat_list.append(item)

    return flat_list


if __name__ == '__main__':

    # Example Usage
    # Define the graph from the given nodes and edges

    file_path = os.path.abspath(r'C:\Users\orman\Documents\MimicHub\Pygorithm\tests\data\test.drawio')
    graph = parse_drawio_file(file_path)
    map_labels_to_edges(graph)
    converter = G2BConverter(graph)
    blocks = converter.graph_to_blocks('2')
    print(blocks)
