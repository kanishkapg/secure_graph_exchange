# ml_core/data_loader.py
import numpy as np

def get_graph_dataset():
    """
    Simulates loading a graph dataset complete with adjacency, 
    and dictionary-based node and edge features for ML training.
    """
    # 1. Adjacency Matrix (Structure of the graph - e.g., 3 nodes)
    adjacency = np.array([
        [0, 1, 1, 1],
        [1, 0, 1, 0],
        [1, 1, 0, 0],
        [1, 0, 0, 0]
    ])
    
    # 2. Node Features using dictionaries with dummy keys
    # Keys are node IDs (0, 1, 2)
    node_features = {
        0: {"type": "C"},
        1: {"type": "H"},
        2: {"type": "N"},
        3: {"type": "O"},
    }
    
    # 3. Edge Features using dictionaries with dummy keys
    # Keys are tuples representing the directed edge (source, target)
    edge_features = {
        (0, 1): {"type": "DOUBLE"},
        (1, 0): {"type": "DOUBLE"},
        (0, 2): {"type": "SINGLE"},
        (2, 0): {"type": "SINGLE"},
        (0, 3): {"type": "SINGLE"},
        (3, 0): {"type": "SINGLE"},
        (1, 2): {"type": "SINGLE"},
        (2, 1): {"type": "SINGLE"}
    }
    
    # Package everything into a single transportable object
    graph_payload = {
        "adjacency": adjacency,
        "node_features": node_features,
        "edge_features": edge_features,
        "metadata": {"nodes": 4, "directed": False, "dataset_name": "Network_Traffic"}
    }
    
    return graph_payload