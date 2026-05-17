import socket
import pickle
import time
import sys
import os

# Add parent directory to path so we can import your crypto modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from ml_core.data_loader import get_graph_dataset
from communication.socket_handler import send_message
from crypto_utils.auth import load_private_key, load_public_key, sign_data
from crypto_utils.encryption import generate_session_key, encrypt_data
from crypto_utils.integrity import generate_data_hash

# Load valid keys
node_a_private = load_private_key("certs/node_a_private.pem")
node_b_public = load_public_key("certs/node_b_public.pem")

print("--- 😈 REPLAY ATTACKER STARTING 😈 ---")
print("[!] Simulating an attacker who captured a valid packet 2 hours ago...")

graph_data = get_graph_dataset()
serialized_graph = pickle.dumps(graph_data)
signature = sign_data(node_a_private, serialized_graph)
data_hash = generate_data_hash(serialized_graph)

# THE ATTACK: Forging an old timestamp to simulate a captured past packet
past_timestamp = time.time() - 7200 # 2 hours ago

payload_dict = {
    'graph_bytes': serialized_graph,
    'signature': signature,
    'hash': data_hash,
    'timestamp': past_timestamp 
}
serialized_payload = pickle.dumps(payload_dict)

session_key = generate_session_key()
encrypted_payload = encrypt_data(serialized_payload, session_key)
encrypted_session_key = node_b_public.encrypt(
    session_key,
    padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
)

print("[!] Sending captured packet to Node B...")
HOST = '127.0.0.1'
PORT = 65432

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        send_message(s, encrypted_session_key)
        send_message(s, encrypted_payload)
except ConnectionRefusedError:
    print("Error: Make sure Node B is running first!")