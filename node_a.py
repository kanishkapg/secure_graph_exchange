import socket
import time
import pickle

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

print("--- NODE A (Data Owner) STARTING ---")
# 2. Extract and format the Graph Dataset
graph_data = get_graph_dataset()
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
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print(f"Connecting to untrusted Model Trainer at {HOST}:{PORT}...")
    s.connect((HOST, PORT))
    
    # Send the encrypted session key first, then the huge payload
    send_message(s, encrypted_session_key)
    send_message(s, encrypted_payload)
    
    print("\n--- SECURE TRANSMISSION COMPLETE ---")
    print("Graph dataset sent securely. Terminating connection.")