import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_and_save_keypair(node_name):
    # Generate RSA Private Key
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    
    # Extract Public Key
    public_key = private_key.public_key()
    
    os.makedirs('certs', exist_ok=True)
    
    # Save Private Key (NEVER SHARE THIS IN REALITY)
    with open(f"certs/{node_name}_private.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
        
    # Save Public Key (Shared with the other peer)
    with open(f"certs/{node_name}_public.pem", "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    print(f"Generated keys for {node_name} in certs/ directory.")

generate_and_save_keypair("node_a")
generate_and_save_keypair("node_b")