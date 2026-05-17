import socket
import pickle
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

from communication.socket_handler import receive_message
from crypto_utils.auth import load_private_key, load_public_key, verify_signature
from crypto_utils.encryption import decrypt_data
from crypto_utils.integrity import verify_data_integrity

# 1. Load Keys (Node B's private key, Node A's public key for authentication)
node_b_private = load_private_key("certs/node_b_private.pem")
node_a_public = load_public_key("certs/node_a_public.pem")

# 2. Setup TCP Server
HOST = '127.0.0.1'
PORT = 65432

print("--- NODE B (Model Trainer) STARTING ---")
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Listening securely on {HOST}:{PORT}...")
    
    conn, addr = s.accept()
    with conn:
        print(f"Connection established with untrusted entity at {addr}")
        
        # 3. Receive the Encrypted Session Key and Payload
        encrypted_session_key = receive_message(conn)
        encrypted_payload = receive_message(conn)
        
        print("Receiving encrypted data...")

        # 4. Decrypt the Session Key using Node B's Private RSA Key (Key Exchange)
        session_key = node_b_private.decrypt(
            encrypted_session_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # 5. Decrypt the Payload using the Session Key (Confidentiality)
        decrypted_payload_bytes = decrypt_data(encrypted_payload, session_key)
        payload = pickle.loads(decrypted_payload_bytes)
        
        # 6. Verify Data Integrity (Hashing)
        if not verify_data_integrity(payload['graph_bytes'], payload['hash']):
            print("CRITICAL ERROR: Data integrity check failed! Connection dropped.")
            exit()
        print("[+] Integrity Verified: Data was not tampered with.")
        
        # 7. Verify Sender Identity (Authentication & Non-repudiation)
        if not verify_signature(node_a_public, payload['signature'], payload['graph_bytes']):
            print("CRITICAL ERROR: Digital signature invalid! Identity spoofed. Connection dropped.")
            exit()
        print("[+] Authentication Verified: Graph data definitely came from Node A.")
        
        # 8. Reconstruct the Graph Dataset for ML Training
        graph_dataset = pickle.loads(payload['graph_bytes'])
        print("\n--- SECURE TRANSMISSION COMPLETE ---")
        print(f"Successfully loaded dataset: {graph_dataset['metadata']['dataset_name']}")
        print(f"Total Nodes: {graph_dataset['metadata']['nodes']}")
        print("Ready for Graph Representation Learning.")