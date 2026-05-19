from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

def load_private_key(filepath):
    """Loads an RSA private key from a PEM file"""
    with open(filepath, "rb") as key_file:
        return serialization.load_pem_private_key(key_file.read(), password=None)

def load_public_key(filepath):
    """Loads an RSA public key from a PEM file"""
    with open(filepath, "rb") as key_file:
        return serialization.load_pem_public_key(key_file.read())

def sign_data(private_key, data_bytes):
    """Creates a digital signature for the data to ensure non-repudiation"""
    signature = private_key.sign(
        data_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def verify_signature(public_key, signature, data_bytes):
    """Verifies the digital signature to authenticate the sender"""
    try:
        public_key.verify(
            signature,
            data_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False # Signature is invalid (spoofed or altered)