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
host = "hourglass-protocol-production.up.railway.app"
port = 5555

class Client:
    def __init__(self, host=host, port=port):
        self.apiManager = APIManager(host, port)
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

#Client()

def connect_to_server(host, port):
    # Create a TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            # Connect to the server
            client_socket.connect((host, port))
            print(f'Connected to server at {host}:{port}')

            # Example of sending a message
            message = "LOGIN"
            client_socket.sendall(message.encode())
            print(f'Sent: {message}')

            # Receiving response from server
            data = client_socket.recv(1024)  # Buffer size is 1024 bytes
            print(f'Received: {data.decode()}')

        except Exception as e:
            print(f'An error occurred: {e}')

if __name__ == "__main__":
    connect_to_server(host, port)