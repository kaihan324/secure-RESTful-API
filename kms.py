import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

BACKEND = default_backend()


MASTER_KEY = os.urandom(32)  # 256-bit key for master encryption

def generate_user_key():

    return os.urandom(32)  # 256-bit user-specific encryption key

def encrypt_key(master_key: bytes, key_to_encrypt: bytes) -> bytes:
  
    iv = os.urandom(16)  # IV for CBC mode
    cipher = Cipher(algorithms.AES(master_key), modes.CBC(iv), backend=BACKEND)
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded = padder.update(key_to_encrypt) + padder.finalize()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    return iv + ciphertext  # Store IV along with the ciphertext

def decrypt_key(master_key: bytes, encrypted_key: bytes) -> bytes:

    iv = encrypted_key[:16]  # Extract IV from the first 16 bytes
    ciphertext = encrypted_key[16:]  # The rest is the encrypted key
    cipher = Cipher(algorithms.AES(master_key), modes.CBC(iv), backend=BACKEND)
    decryptor = cipher.decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    return unpadder.update(padded) + unpadder.finalize()

def save_encrypted_key(user_id: int, encrypted_key: bytes):
 
    with open(f"user_{user_id}_key.enc", "wb") as f:
        f.write(encrypted_key)

def load_encrypted_key(user_id: int) -> bytes:
    
    with open(f"user_{user_id}_key.enc", "rb") as f:
        return f.read()

def encrypt_data(user_key: bytes, plaintext: bytes) -> bytes:
    
    iv = os.urandom(16)  # IV for CBC mode
    cipher = Cipher(algorithms.AES(user_key), modes.CBC(iv), backend=BACKEND)
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded = padder.update(plaintext) + padder.finalize()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    return iv + ciphertext  # Store IV along with the ciphertext

def decrypt_data(user_key: bytes, encrypted_data: bytes) -> bytes:

    iv = encrypted_data[:16]  # Extract IV from the first 16 bytes
    ciphertext = encrypted_data[16:]  # The rest is the encrypted data
    cipher = Cipher(algorithms.AES(user_key), modes.CBC(iv), backend=BACKEND)
    decryptor = cipher.decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    return unpadder.update(padded) + unpadder.finalize()

