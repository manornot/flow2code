import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))


decision_node = {
    "geometry": {"x": 100, "y": 100, "width": 50, "height": 50}
}
edges = [
    {"id": "edge1", "source_geometry": {"x": 125, "y": 90}},  # Top
    {"id": "edge2", "source_geometry": {"x": 125, "y": 160}},  # Bottom
]
text_blocks = {
    "text1": {"label": "Yes", "geometry": {"x": 120, "y": 50, "width": 30, "height": 20}},
    "text2": {"label": "No", "geometry": {"x": 120, "y": 170, "width": 30, "height": 20}},
    "text3": {"label": "Maybe", "geometry": {"x": 200, "y": 100, "width": 30, "height": 20}},
}

from src.utils.matching import find_nearest_text_blocks
from src.utils.matching import map_labels_to_edges

matched = map_labels_to_edges#find_nearest_text_blocks(decision_node, edges, text_blocks)
print(matched)
