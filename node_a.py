import socket
import time
import pickle
import matplotlib.pyplot as plt
import networkx as nx
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

from ml_core.data_loader import get_graph_dataset
from communication.socket_handler import send_message
from crypto_utils.auth import load_private_key, load_public_key, sign_data
from crypto_utils.encryption import generate_session_key, encrypt_data
from crypto_utils.integrity import generate_data_hash

# 1. Load Keys (Node A's private key for signing, Node B's public key for key exchange)
node_a_private = load_private_key("certs/node_a_private.pem")
node_b_public = load_public_key("certs/node_b_public.pem")


def visualize_reconstructed_graph(graph_data):
    """Visualizes the successfully transmitted graph dataset."""
    print("Visualizing the reconstructed graph...")

    # 1. Create a NetworkX graph from the adjacency matrix
    adjacency = graph_data['adjacency']

    G = nx.from_numpy_array(
        adjacency,
        create_using=nx.DiGraph if graph_data['metadata']['directed'] else nx.Graph
    )

    # 2. Map the node features back to the graph nodes
    node_features = graph_data['node_features']
    nx.set_node_attributes(G, node_features)

    edge_features = graph_data['edge_features']
    nx.set_edge_attributes(G, edge_features)

    # 3. Prepare edge weights based on edge type
    edge_widths = []
    edge_labels = {}

    for u, v, data in G.edges(data=True):
        edge_type = data.get("type", "NORMAL")

        # Store edge label
        edge_labels[(u, v)] = edge_type

        # Increase width for DOUBLE edges
        if edge_type == "DOUBLE":
            edge_widths.append(4.0)
        else:
            edge_widths.append(1.5)

    # 4. Draw the graph
    plt.figure(figsize=(8, 6))

    # Create labels showing the Node ID and its type
    labels = {
        node: data.get('type', 'Unknown')
        for node, data in G.nodes(data=True)
    }

    # Use spring layout
    pos = nx.spring_layout(G, seed=42)

    # Draw nodes and edges
    nx.draw(
        G,
        pos,
        labels=labels,
        with_labels=True,
        node_color='lightgreen',
        node_size=2500,
        font_size=10,
        font_weight='bold',
        edge_color='gray',
        width=edge_widths
    )

    # Draw edge labels
    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        font_color='red',
        font_size=9
    )

    plt.title(f"Sending Graph: {graph_data['metadata']['dataset_name']}")
    plt.axis('off')
    plt.show()

print("--- NODE A (Data Owner) STARTING ---")
# 2. Extract and format the Graph Dataset
graph_data = get_graph_dataset()
visualize_reconstructed_graph(graph_data)
serialized_graph = pickle.dumps(graph_data)
print(f"Loaded Graph Dataset: {graph_data['metadata']['dataset_name']}")

# 3. Apply Security Properties
# Authentication / Non-repudiation: Sign the data
signature = sign_data(node_a_private, serialized_graph)

# Integrity: Hash the data
data_hash = generate_data_hash(serialized_graph)

# Package it all together
payload_dict = {
    'graph_bytes': serialized_graph,
    'signature': signature,
    'hash': data_hash,
    'timestamp': time.time()
}
serialized_payload = pickle.dumps(payload_dict)

# Confidentiality: Encrypt the payload with a fast symmetric session key
session_key = generate_session_key()
encrypted_payload = encrypt_data(serialized_payload, session_key)

# Key Exchange: Encrypt the session key with Node B's public RSA key
encrypted_session_key = node_b_public.encrypt(
    session_key,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

print("[+] Dataset securely hashed, signed, and encrypted.")

# 4. Transmit over TCP Socket
HOST = '127.0.0.1'
PORT = 65431

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print(f"Connecting to untrusted Model Trainer at {HOST}:{PORT}...")
    s.connect((HOST, PORT))
    
    # Send the encrypted session key first, then the huge payload
    send_message(s, encrypted_session_key)
    send_message(s, encrypted_payload)
    
    print("\n--- SECURE TRANSMISSION COMPLETE ---")
    print("Graph dataset sent securely. Terminating connection.")