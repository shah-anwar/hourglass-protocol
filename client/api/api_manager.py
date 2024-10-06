# takes in packets and decides if sent to circuit handler (sending messages as self, or redirecting as an internal node)
# or send packets directly to server as the exit node of a circuit
from .circuit_handler import CircuitHandler
from .exit_node_handler import ExitNodeHandler
from .origin_node_handler import OriginNodeHandler

from .packet_handler import process_packet
from .packet_builder import PacketBuilder

from cryptography.hazmat.primitives.asymmetric import rsa

import asyncio, socket

class APIManager:
    def __init__(self, server_ip, server_port):
        self.circuits = {}
        self.exits = {}
        self.origin = None

        self.packet_builder = PacketBuilder()

        self.server_ip = server_ip
        self.server_port = server_port

        self.client_ip = '127.0.0.1'
        self.client_port = 123

        self.reader = None
        self.writer = None

    # circuit initialisation methods

    async def new_origin(self, circuit_id: bytes):
        ip_list = self.get_ips(5)
        self.origin = OriginNodeHandler(circuit_id, ip_list)

    def get_ips(self, amount: int):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.server_ip, self.server_port))
            message = f"GETIPS~~{amount}"
            s.sendall(message.encode())
            response = s.recv(1024)
        
        response = response.decode()

        if response == "DATABASE_EMPTY":
            print("There are no connectable users.")
            return []

        ip_list = response.split("~~")
        print(ip_list)
        return ip_list

    # asynchronous methods for average running

    async def handle_incoming_requests(self):
        server = await asyncio.start_server(self.handle_node, self.client_ip, self.client_port)

        async with server:
            print(f"Listening for join requests on {self.client_ip}:{self.client_port}")
            await server.serve_forever()

    async def handle_node(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        back_node_ip = writer.get_extra_info('peername')
        print(f"New connection from {back_node_ip}")

        try:
            data = await reader.read(1024)
            if not data:
                print(f"No data from {back_node_ip}. Closing.")
            
            packet = data.decode().strip()
            print(f"Received packet from {back_node_ip}")

            header, result = process_packet(packet)
            if header == "JOIN":
                self.join_circuit(result, reader, writer)
        
        except Exception as e:
            print(f"Error while handling node {back_node_ip}: {e}")
        
        finally:
            print(f"Closing connection with {back_node_ip}")
            writer.close()
            await writer.wait_closed()

    async def join_circuit(self, result, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        circuit_id = str(result[0])
        back_public_key = result[1]
        forwards_private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048,
                )
        
        response = self.packet_builder.join_ack(circuit_id, forwards_private_key, back_public_key)
        writer.write(response)
        await writer.drain()
        
        ip_list = self.get_ips(5)
        self.circuits[circuit_id] = CircuitHandler(circuit_id, ip_list, (reader, writer), forwards_private_key, back_public_key)