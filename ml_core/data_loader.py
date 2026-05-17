# ml_core/data_loader.py
import numpy as np

def get_graph_dataset():
    """
    Simulates loading a graph dataset complete with adjacency, 
    and dictionary-based node and edge features for ML training.
    """
    # 1. Adjacency Matrix (Structure of the graph - e.g., 3 nodes)
    adjacency = np.array([
        [0, 1, 0],
        [1, 0, 1],
        [0, 1, 0]
    ])
    
    # 2. Node Features using dictionaries with dummy keys
    # Keys are node IDs (0, 1, 2)
    node_features = {
        0: {"type": "client", "trust_score": 0.95, "active_sessions": 4},
        1: {"type": "router", "trust_score": 0.50, "active_sessions": 12},
        2: {"type": "server", "trust_score": 0.99, "active_sessions": 105}
    }
    
    # 3. Edge Features using dictionaries with dummy keys
    # Keys are tuples representing the directed edge (source, target)
    edge_features = {
        (0, 1): {"weight": 1.5, "protocol": "TCP", "encrypted": True},
        (1, 0): {"weight": 1.5, "protocol": "TCP", "encrypted": True},
        (1, 2): {"weight": 0.9, "protocol": "UDP", "encrypted": False},
        (2, 1): {"weight": 0.9, "protocol": "UDP", "encrypted": False}
    }
    
    # Package everything into a single transportable object
    graph_payload = {
        "adjacency": adjacency,
        "node_features": node_features,
        "edge_features": edge_features,
        "metadata": {"nodes": 3, "directed": False, "dataset_name": "Network_Traffic_V1"}
    }
    
    return graph_payload