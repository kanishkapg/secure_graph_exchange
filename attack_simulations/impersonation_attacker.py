import socket
import pickle
import time
import sys, os

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_core.data_loader import get_graph_dataset
from communication.socket_handler import send_message
from crypto_utils.auth import load_public_key, sign_data
from crypto_utils.encryption import generate_session_key, encrypt_data
from crypto_utils.integrity import generate_data_hash

# The attacker only has Node B's public key (which is public anyway)
node_b_public = load_public_key("certs/node_b_public.pem")

print("--- 😈 IMPERSONATION ATTACKER STARTING 😈 ---")
print("[!] Generating fake RSA keys to pretend to be Node A...")
# Attacker generates a FAKE private key on the fly
fake_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

graph_data = get_graph_dataset()
serialized_graph = pickle.dumps(graph_data)

# Attacker signs the data with their FAKE key
signature = sign_data(fake_private_key, serialized_graph)
data_hash = generate_data_hash(serialized_graph)

payload_dict = {
    'graph_bytes': serialized_graph,
    'signature': signature,
    'hash': data_hash,
    'timestamp': time.time() # Valid timestamp, so it passes the replay check
}
serialized_payload = pickle.dumps(payload_dict)

session_key = generate_session_key()
encrypted_payload = encrypt_data(serialized_payload, session_key)
encrypted_session_key = node_b_public.encrypt(
    session_key,
    padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
)

print("[!] Attempting to send poisoned dataset to Node B disguised as Node A...")
HOST = '127.0.0.1'
PORT = 65432

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        send_message(s, encrypted_session_key)
        send_message(s, encrypted_payload)
except ConnectionRefusedError:
    print("Error: Make sure Node B is running first!")