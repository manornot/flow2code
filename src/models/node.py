from pydantic import BaseModel
from typing import List


class Geometry(BaseModel):
    x: float
    y: float
    width: float
    height: float  


class Node(BaseModel):
    node_id: str =''
    type: str =''
    label: str = ''
    geometry: Geometry
    edges: List[str] = []
    neighbors: List[str] = []

    def __init__(self, **data):
        if 'geometry' in data and isinstance(data['geometry'], dict):
            data['geometry'] = Geometry(**data['geometry'])
        super().__init__(**data)

    def __hash__(self):
        # Hash by `node_id` for consistency
        return hash(self.node_id)

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.node_id == other.node_id
    

class Block:
    """
    Represents a block in the Python code with attributes derived from the graph.
    """
    def __init__(self, node: Node):
        self.node = node

    def generate_code(self) -> str:
        """
        Abstract method to generate code for this block. Implemented in subclasses.
        """
        raise NotImplementedError("Subclasses must implement generate_code()")