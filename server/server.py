import socket
import asyncio
import zmq
import zmq.asyncio

from .packet_handler import PacketHandler
from .redis_client import RedisClient
from .mongodb_client import MongoDBClient

class Server:
    def __init__(self):
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:5555")
        self.packet_handler = PacketHandler()

    async def listen_for_packets(self):
        while True:
            packet = await self.socket.recv()
            print(f"Received packet: {packet}")

            response = self.packet_handler.handle_packet(packet)
            await self.socket.send(response)

async def main():
    server = Server()
    await server.listen_for_packets()

if __name__ == "__main__":
    asyncio.run(main())