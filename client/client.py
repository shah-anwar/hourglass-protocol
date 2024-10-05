import socket, multiprocessing, asyncio, os, time
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asymmetric_padding
from cryptography.hazmat.backends import default_backend
from packet_builder import PacketBuilder
import packet_handler as PacketHandler
from api.api_manager import APIManager

USER_IP = None
server = "tcp://hourglass-protocol-production.up.railway.app"
server_port = 5555

class Client:
    def __init__(self, host='127.0.0.1', port=123):
        self.apiManager = APIManager(server, server_port)
        message = self.start_circuit()
        print(PacketHandler.process_packet(message))

    def start_circuit(self):
        circuit_id = bytes.fromhex(os.urandom(8).hex()) # random 30digit hex string
        circuit_private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        message = PacketBuilder.join_request(circuit_id, circuit_private_key)
        self.apiManager.new_origin(circuit_id, message)

    def register(self, username, private_key):
        pass

    def login(self, username, private_key):
        pass

    def send(self, message, destination):
        pass

Client()