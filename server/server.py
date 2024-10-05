import socket
import asyncio
import os

from .packet_handler import PacketHandler
from .redis_client import RedisClient
from .mongodb_client import MongoDBClient

packet_handler = PacketHandler()

#port = os.environ.get("PORT", "5555")
port = "5555"

async def handle_client(reader, writer):
    address = writer.get_extra_info("peername")
    print(f"Connection from {address}")

    while True:
        try:
            data = await reader.read(100)
            if not data:
                break

            message = data.decode()
            print(f"Received {message}")
            
            response = packet_handler.handle_packet(message)
            writer.write(response.encode())
            await writer.drain()

        except ConnectionResetError:
            print(f"Connection closed by {address}")
            break
    
    print(f"Closing connection from {address}")
    writer.close()
    await writer.wait_closed()
        
async def start_server():
    server = await asyncio.start_server(handle_client, '0.0.0.0', 5555)
    addr = server.sockets[0].getsockname()
    print(f"Server started at {addr}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(start_server())