import socket
import pickle
import time
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import InvalidToken # Add this to your imports at the top!

from communication.socket_handler import receive_message
from crypto_utils.auth import load_private_key, load_public_key, verify_signature
from crypto_utils.encryption import decrypt_data
from crypto_utils.integrity import verify_data_integrity

node_b_private = load_private_key("certs/node_b_private.pem")
node_a_public = load_public_key("certs/node_a_public.pem")

HOST = '127.0.0.1'
PORT = 65432

import networkx as nx
import matplotlib.pyplot as plt


def visualize_reconstructed_graph(graph_data):
    """Visualizes the successfully transmitted graph dataset."""
    print("Visualizing the reconstructed graph...")

    adjacency = graph_data['adjacency']

    G = nx.from_numpy_array(
        adjacency,
        create_using=nx.DiGraph if graph_data['metadata']['directed'] else nx.Graph
    )

    node_features = graph_data['node_features']
    nx.set_node_attributes(G, node_features)

    edge_features = graph_data['edge_features']
    nx.set_edge_attributes(G, edge_features)

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

    plt.title(f"Securely Received Graph: {graph_data['metadata']['dataset_name']}")
    plt.axis('off')
    plt.show()


print("NODE B (Model Trainer) STARTING")
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Listening securely on {HOST}:{PORT}")
    
    conn, addr = s.accept()
    with conn:
        print(f"Connection established with untrusted entity at {addr}")
        
        encrypted_session_key = receive_message(conn)
        encrypted_payload = receive_message(conn)
        
        print("Receiving encrypted data...")

        try:
            session_key = node_b_private.decrypt(
                encrypted_session_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            decrypted_payload_bytes = decrypt_data(encrypted_payload, session_key)
            payload = pickle.loads(decrypted_payload_bytes)
            
            MAX_TIME_DIFF = 60 # Packets older than 60 seconds are rejected
            current_time = time.time()
            if current_time - payload.get('timestamp', 0) > MAX_TIME_DIFF:
                print("\nSECURITY ALERT: REPLAY ATTACK DETECTED!")
                print("The packet is too old. It was likely captured and resent by an attacker.")
                print("Connection terminated.")
                exit()
            print("[+] Freshness Verified: Packet is recent (Replay Attack mitigated).")
            
        except InvalidToken:
            print("\nSECURITY ALERT: MITM ATTACK DETECTED!")
            print("The encrypted payload was tampered with during transmission.")
            print("Decryption failed. Connection terminated to protect system integrity.")
            exit()
        except Exception as e:
            print(f"\nSECURITY ALERT: Unknown decryption error: {e}")
            exit()
            
        if not verify_data_integrity(payload['graph_bytes'], payload['hash']):
            print("CRITICAL ERROR: Data integrity check failed! Connection dropped.")
            exit()
        print("[+] Integrity Verified: Data was not tampered with.")
        
        if not verify_signature(node_a_public, payload['signature'], payload['graph_bytes']):
            print("CRITICAL ERROR: Digital signature invalid! Identity spoofed. Connection dropped.")
            exit()
        print("[+] Authentication Verified: Graph data definitely came from Node A.")
        
        graph_dataset = pickle.loads(payload['graph_bytes'])
        visualize_reconstructed_graph(graph_dataset)
        print("\nSECURE TRANSMISSION COMPLETE")
        print(f"Successfully loaded dataset: {graph_dataset['metadata']['dataset_name']}")
        print(f"Total Nodes: {graph_dataset['metadata']['nodes']}")
        print("Ready for Graph Representation Learning.")

