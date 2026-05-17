# crypto_utils/integrity.py
import hashlib

def generate_data_hash(data_bytes):
    """Generates a SHA-256 hash of the data payload"""
    # We use SHA-256 to create a unique 'fingerprint' of the graph data
    digest = hashlib.sha256(data_bytes).hexdigest()
    return digest

def verify_data_integrity(data_bytes, received_hash):
    """Checks if the recalculated hash matches the received hash"""
    calculated_hash = generate_data_hash(data_bytes)
    return calculated_hash == received_hash