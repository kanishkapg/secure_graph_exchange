import numpy as np

def get_graph_dataset():
    adjacency = np.array([
        [0, 1, 1, 1],
        [1, 0, 1, 0],
        [1, 1, 0, 0],
        [1, 0, 0, 0]
    ])

    node_features = {
        0: {"type": "C"},
        1: {"type": "H"},
        2: {"type": "N"},
        3: {"type": "O"},
    }

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
    
    graph_payload = {
        "adjacency": adjacency,
        "node_features": node_features,
        "edge_features": edge_features,
        "metadata": {"nodes": 4, "directed": False, "dataset_name": "Network_Traffic"}
    }
    
    return graph_payload