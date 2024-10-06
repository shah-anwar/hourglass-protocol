import socket, multiprocessing, asyncio, os, time
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asymmetric_padding
from cryptography.hazmat.backends import default_backend
from api.api_manager import APIManager

USER_IP = None

#server details
host = "0.0.0.0"
port = 12345

class Client:
    def __init__(self, host=host, port=port):
        self.api_manager = APIManager(host, port)
        asyncio.run(self.start_circuit())

    #starting circuits

    async def start_circuit(self):
        circuit_id = bytes.fromhex(os.urandom(8).hex()) # random 30digit hex string
        await self.api_manager.new_origin(circuit_id)

    #using circuits

    async def register(self, username, private_key):
        pass

    async def login(self, username, private_key):
        pass

    async def send(self, message, destination):
        pass

    #joining circuits

    async def start_listener(self):
        await self.api_manager.handle_incoming_requests()

    async def run(self):
        await self.start_listener()

if __name__ == "__main__":
    client = Client()
    asyncio.run(client.run())