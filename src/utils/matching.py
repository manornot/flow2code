import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import numpy as np
from src.parser.drawio_parser import parse_drawio_file

import math
import logging
import coloredlogs
# Configure logging
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', fmt='%(hostname)s %(name)s[%(process)d] %(levelname)s %(message)s')

def convert_x_value(value):
    if value > 0:
        return 0
    elif value == 0:
        return 0.5
    else:  # value < 0
        return 1
    
def convert_y_value(value):
    if value > 0:
        return 1
    elif value == 0:
        return 0.5
    else:  # value < 0
        return 0
def map_labels_to_edges(graph) -> None:
    nodes = graph.nodes
    edges = graph.edges
    decision_nodes = {node_id: data for node_id, data in nodes.items() if data["type"] == "decision"}
    text_blocks = {node_id: data for node_id, data in nodes.items() if data["type"] == "text"}
    decision_nodes_neighbours = {node_id: list(graph.neighbors(node_id)) for node_id in decision_nodes}

    
    #sellect two nearest to target text_blocks
    for block in text_blocks:
        dec_candidates = {
            dec_node:np.linalg.norm(
                np.asanyarray(
                    [nodes[dec_node]['geometry']['x'],
                     nodes[dec_node]['geometry']['y']]
                    )-np.asanyarray(
                        [text_blocks[block]['geometry']['x'],
                         text_blocks[block]['geometry']['y']]
                        )) for dec_node in decision_nodes}
        text_blocks[block]['decision'] = list(sorted(dec_candidates.items(),key=lambda item:item[1]))[0][0]
    
    
    
    for src in decision_nodes_neighbours:
        src_edges = {}
        for trgt in decision_nodes_neighbours[src]:
            edge = extract_edge_exit_point(edges[(src, trgt)])
            
            if edge == {'exitX':0.5, 'exitY':0.5}:
                src_pos = np.asanyarray([nodes[src]['geometry']['x'],nodes[src]['geometry']['y']])
                trgt_pos = np.asanyarray([nodes[trgt]['geometry']['x'],nodes[trgt]['geometry']['y']])
                vec = src_pos - trgt_pos
                edge = {'exitX':convert_x_value(vec[0]), 'exitY':convert_y_value(vec[1])}
            src_edges[trgt] = edge
        
        src_text_blocks = {text_blocks[block]['label']:text_blocks[block] for block in text_blocks if text_blocks[block]['decision'] == src}
        src_edges = {trgt:relative2absolute(src_edges[trgt],decision_nodes[src]) for trgt in src_edges}
        already_used_labels = set()
        for trgt in src_edges:
            distances = {block:np.linalg.norm(
                np.asanyarray(
                    [
                        src_text_blocks[block]['geometry']['x']+0.5*src_text_blocks[block]['geometry']['width'],
                        src_text_blocks[block]['geometry']['y']+0.5*src_text_blocks[block]['geometry']['height'],
                        ]
                    )-np.asanyarray(
                        [
                            src_edges[trgt]['exitX'], 
                            src_edges[trgt]['exitY']
                            ]
                        )) for block in src_text_blocks}
            #src_text_blocks.sort(key=lambda block: np.linalg.norm(np.asanyarray([block['geometry']['x'], block['geometry']['y']])-np.asanyarray([decision_nodes[src]['geometry']['x'], decision_nodes[src]['geometry']['y']])))

            graph.edges[(src, trgt)]['label'] = min(distances, key=distances.get)
            #print(f'Edge {src}->{trgt} label: {graph.edges[(src, trgt)]["label"]}')
    classify_loops(graph)
    classify_edges(graph)

def relative2absolute(edge,node):
    edge = {'exitX': edge['exitX']*node['geometry']['width'] + node['geometry']['x'], 'exitY': edge['exitY']*node['geometry']['height'] + node['geometry']['y']}
    return edge
    

def extract_edge_exit_point(cell):
    """
    Extracts the exitX and exitY attributes from a cell's style.
    """
    style = cell.get('style', '')
    exitX, exitY = 0.5, 0.5  # Defaults
    for item in style.split(';'):
        if item.startswith('exitX='):
            exitX = float(item.split('=')[1])
        elif item.startswith('exitY='):
            exitY = float(item.split('=')[1])
    return {'exitX': exitX, 'exitY': exitY}

def classify_edges(graph):
    for edge in graph.edges(data=True):
        source, target, data = edge
        source_node = graph.nodes[source]
        target_node = graph.nodes[target]
        
        if source_node['type'] in ('repeat_loop', 'for_each_loop'):
            # Try to use exitX and exitY
            exit_point = extract_edge_exit_point(data)
            if exit_point.get('exitX') is not None and exit_point.get('exitY') is not None:
                if exit_point['exitX'] == 0.5 and exit_point['exitY'] == 1:
                    data['role'] = 'body'
                elif exit_point['exitX'] == 1 and exit_point['exitY'] == 0.5:
                    data['role'] = 'exit'
                else:
                    # Fallback to relative position
                    source_geom = source_node.get('geometry', {})
                    target_geom = target_node.get('geometry', {})
                    source_x = source_geom.get('x', 0)
                    source_y = source_geom.get('y', 0)
                    target_x = target_geom.get('x', 0)
                    target_y = target_geom.get('y', 0)
                    
                    if target_y > source_y and abs(target_x - source_x) < target_geom.get('width', 0) / 2:
                        data['role'] = 'body'  # Below the source (vertical alignment)
                    elif target_x > source_x and abs(target_y - source_y) < target_geom.get('height', 0) / 2:
                        data['role'] = 'exit'  # To the right of the source (horizontal alignment)
                    else:
                        data['role'] = 'unknown'

        elif source_node['type'] == 'process':
            data['role'] = 'u_def'
        elif source_node['type'] == 'while_loop':
            if data['label'].lower() in ('true', 'yes'):
                data['role'] = 'body'
            elif data['label'].lower() in ('false', 'no'):
                data['role'] = 'exit'
            else:
                data['role'] = 'unknown'
        elif source_node['type'] == 'decision':
            if data['label'].lower() in ('yes', 'true'):
                data['role'] = 'true branch'
            elif data['label'].lower() in ('no', 'false'):
                data['role'] = 'false branch'
            else:
                data['role'] = 'unknown'
                

def dfs(graph, start_node,current_node,visited):
        if current_node in visited:
            return False  # Already visited
        if current_node == start_node:
            return True  # Cycle detected
        visited.add(current_node)
        for successor in graph.successors(current_node):
            if dfs(graph,start_node,successor,visited):
                return True
        return False
    
def exits_loop(graph, start_node,current_node,visited):
    if current_node in visited:
        return False  # Avoid cycles in traversal
    visited.add(current_node)
    for successor in graph.successors(current_node):
        if any([graph.nodes[sccsr]['type'] in ('repeat_loop','for_each_loop') for sccsr in graph.successors(start_node)]):
            if graph.edges[(start_node, current_node)]['label'].lower() == 'no':
                return True
        if graph.nodes[current_node]['type'] in ['repeat_loop', 'while_loop', 'for_each_loop']:
            if graph.edges[(current_node,successor)]['role'] == 'body':
                continue
        if successor == start_node:
            return False  # False branch cannot loop back
        if not exits_loop(graph, start_node,successor,visited):
            return False
    return True

def classify_loops(graph):
    for node in graph.nodes():
        if graph.nodes[node]['type'] == 'decision':
            true_branch = None
            
            for successor, edge_data in graph[node].items():
                label = edge_data.get('label', '').lower()
                if label in ['yes', 'true']:
                    true_branch = successor
                elif label in ['no', 'false']:
                    false_branch = successor
            visited = set()
            if dfs(graph, node, true_branch, visited):
                visited.clear()
                if exits_loop(graph, node, false_branch, visited):
                    graph.nodes[node]['type'] = 'while_loop'
    
            
if __name__ == "__main__":
    file_path = os.path.abspath(r'C:\Users\orman\Documents\MimicHub\Pygorithm\tests\data\test.drawio')
    graph = parse_drawio_file(file_path)
    map_labels_to_edges(graph)
    print('here')

