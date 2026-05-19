from cryptography.fernet import Fernet

def generate_session_key():
    """Generates a secure symmetric key for the session"""
    return Fernet.generate_key()

def encrypt_data(data_bytes, key):
    """Encrypts raw bytes using the provided key"""
    f = Fernet(key)
    encrypted_data = f.encrypt(data_bytes)
    return encrypted_data

def decrypt_data(encrypted_bytes, key):
    """Decrypts bytes back to original form"""
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_bytes)
    return decrypted_data