# mitm_proxy.py
import socket

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from communication.socket_handler import receive_message, send_message

# The proxy poses as the server to Node A
PROXY_HOST = '127.0.0.1'
PROXY_PORT = 65431  # Different port!

# The proxy connects to the real Node B
TARGET_HOST = '127.0.0.1'
TARGET_PORT = 65432

print("--- 😈 MALICIOUS MITM PROXY STARTING 😈 ---")
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_server:
    proxy_server.bind((PROXY_HOST, PROXY_PORT))
    proxy_server.listen()
    print(f"Proxy listening on {PROXY_HOST}:{PROXY_PORT}...")
    
    # 1. Accept connection from Node A
    conn_a, addr_a = proxy_server.accept()
    with conn_a:
        print(f"[!] Intercepted connection from Node A at {addr_a}")
        
        # 2. Connect to the real Node B
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_b:
            sock_b.connect((TARGET_HOST, TARGET_PORT))
            print("[!] Connected to real Node B. Forwarding data...")
            
            # 3. Intercept the Session Key and forward it untouched
            encrypted_session_key = receive_message(conn_a)
            send_message(sock_b, encrypted_session_key)
            print("[!] Intercepted and forwarded Session Key.")
            
            # 4. Intercept the Encrypted Payload
            encrypted_payload = receive_message(conn_a)
            print(f"[!] Intercepted Encrypted Payload. Size: {len(encrypted_payload)} bytes.")
            
            # 5. THE ATTACK: Modify the ciphertext!
            # We change the last byte of the encrypted payload to simulate data tampering
            malicious_payload = bytearray(encrypted_payload)
            malicious_payload[-1] = malicious_payload[-1] ^ 0xFF # Flip bits
            
            print("[!] 😈 Tampering with payload ciphertext...")
            
            # 6. Send the tampered payload to Node B
            send_message(sock_b, bytes(malicious_payload))
            print("[!] Forwarded tampered payload to Node B. Waiting for fireworks...")