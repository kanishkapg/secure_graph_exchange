# test_crypto.py
import numpy as np
import pickle
from crypto_utils.encryption import generate_session_key, encrypt_data, decrypt_data
from crypto_utils.integrity import generate_data_hash, verify_data_integrity

print("--- 1. PREPARING GRAPH DATA (NODE A) ---")
# Simulating a graph adjacency matrix or sparse dictionary (FYP related)
graph_matrix = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
print(f"Original Graph Matrix:\n{graph_matrix}\n")

# Serialize the NumPy array into bytes
serialized_graph = pickle.dumps(graph_matrix)

print("--- 2. APPLYING SECURITY MEASURES (NODE A) ---")
# Generate a shared session key (in reality, established via Key Exchange)
session_key = generate_session_key()

# Hash the serialized data for Integrity
data_hash = generate_data_hash(serialized_graph)
print(f"Data SHA-256 Hash: {data_hash}")

# Encrypt the serialized data for Confidentiality
encrypted_payload = encrypt_data(serialized_graph, session_key)
print(f"Encrypted Payload (first 50 bytes): {encrypted_payload[:50]}...\n")


print("--- 3. RECEIVING AND VERIFYING (NODE B) ---")
# Node B decrypts the payload
decrypted_bytes = decrypt_data(encrypted_payload, session_key)

# Node B verifies the integrity using the hash
is_valid = verify_data_integrity(decrypted_bytes, data_hash)

if is_valid:
    print("Integrity Check Passed: Data was not tampered with!")
    # Deserialize the bytes back into the NumPy array
    received_graph = pickle.loads(decrypted_bytes)
    print(f"Recovered Graph Matrix:\n{received_graph}")
    
    # Verify it perfectly matches the original
    if np.array_equal(graph_matrix, received_graph):
        print("\nSuccess! The graph data was securely encrypted, hashed, transmitted, and recovered.")
else:
    print("Integrity Check Failed: The data was corrupted or altered!")