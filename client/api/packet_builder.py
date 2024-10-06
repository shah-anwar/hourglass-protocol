import time, os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asymmetric_padding
from cryptography.hazmat.backends import default_backend
import base64

delim = b"~~" #delimiter

def encrypt_aes(message, key):
    iv = os.urandom(16)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(message) + padder.finalize()

    encrypted_message = encryptor.update(padded_data) + encryptor.finalize()

    return iv + encrypted_message

def sign_message(private_key, message):
    signature = private_key.sign(
        message,
        asymmetric_padding.PSS(
            mgf=asymmetric_padding.MGF1(hashes.SHA256()),
            salt_length=asymmetric_padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

class PacketBuilder:

    @staticmethod
    def join_request(circuit_id, circuit_private_key):
        HEADER = b"JOIN" + delim + circuit_id + delim
        timestamp = str(time.time()).encode() + delim
        
        circuit_public_key_pem = circuit_private_key.public_key().public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )

        join_message = HEADER + timestamp + circuit_public_key_pem
        signature = sign_message(circuit_private_key, join_message)
        signed_message = join_message + delim + signature
        return signed_message

    def join_ack(circuit_id, forwards_private_key, back_public_key):
        HEADER = b"JOIN_ACK" + delim + circuit_id + delim
        timestamp = str(time.time()).encode() + delim

        forwards_public_key_pem = forwards_private_key.public_key().public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
        
        join_message = HEADER + timestamp + forwards_public_key_pem
        signature = sign_message(forwards_private_key, join_message)
        signed_message = join_message + delim + signature

        aes_key = os.urandom(32)
        encrypted_message = encrypt_aes(signed_message, aes_key)
        encrypted_aes_key = back_public_key.encrypt(
                    aes_key,
                    asymmetric_padding.OAEP(
                        mgf=asymmetric_padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
        final_message = encrypted_message + encrypted_aes_key

        return final_message

    
    def exit_ack():
        HEADER = b"EXIT_ACK:"

    def register(username, private_key):
        pass
    
    def login():
        pass
        
    def message():
        pass