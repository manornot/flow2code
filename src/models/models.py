from typing import List, Optional
from pydantic import BaseModel

class Geometry(BaseModel):
    x: float
    y: float
    width: float
    height: float

class Node(BaseModel):
    node_id: str = '-1'
    type: str = ''
    label: str = ''
    geometry: Geometry = Geometry(x=0, y=0, width=-1, height=-1)
    edges: List[str] = []  # IDs of connected edges
    neighbors: List[str] = []  # IDs of neighboring nodes

    def __hash__(self):
        return hash(self.node_id)

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.node_id == other.node_id

class Edge(BaseModel):
    edge_id: str
    source: str  # ID of the source node
    target: str  # ID of the target node
