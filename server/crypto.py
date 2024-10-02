from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import os
import base64

# Generate and Encrypting Private Key

def generateKeys():
    private_key = rsa.generate_private_key(65537, 2048)
    return private_key, private_key.public_key()

def getKeyAsBytes(private_key):
    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption())
    return private_key_bytes

def deriveKey(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # AES-256 key
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def encryptKey(private_key_bytes, password):
    salt = os.urandom(16)
    aesgcm = AESGCM(deriveKey(password, salt))
    nonce = os.urandom(12)
    encrypted_key = aesgcm.encrypt(nonce, private_key_bytes, None)

    return base64.b64encode(salt + nonce + encrypted_key).decode('utf-8')
        
# Decrypting Private Keys
def decryptKey(encrypted_private_key_b64, password):
    encrypted_data = base64.b64decode(encrypted_private_key_b64)

    salt = encrypted_data[:16]
    nonce = encrypted_data[16:28]
    encrypted_private_key = encrypted_data[28:]

    aesgcm = AESGCM(deriveKey(password, salt))
    decrypted_key = aesgcm.decrypt(nonce, encrypted_private_key, None)
    
    private_key = load_pem_private_key(
    decrypted_key,
    password=None,  # We already decrypted it
    backend=default_backend()
    )
    
    return private_key