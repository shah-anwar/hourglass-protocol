import socket
import asyncio
import os

from packet_handler import PacketHandler
from mongodb_client import MongoDBClient

packet_handler = PacketHandler()

port = os.environ.get("PORT", "12345")


async def handle_client(reader, writer):
    address = writer.get_extra_info("peername")
    print(f"Connection from {address}")

    while True:
        try:
            data = await reader.read(100)
            if not data:
                break

            print(f"Received {data.decode()}")
            
            response = packet_handler.process_packet(data, address)
            print(f"Returning {response.decode()}")
            writer.write(response)
            await writer.drain()

        except ConnectionResetError:
            print(f"Connection closed by {address}")
            break
    
    print(f"Closing connection from {address}")
    writer.close()
    await writer.wait_closed()
        
async def start_server():
    server = await asyncio.start_server(handle_client, '0.0.0.0', port)
    addr = server.sockets[0].getsockname()
    print(f"Server started at {addr}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(start_server())