import asyncio
from server.server import main as server_main

if __name__ == "main":
    asyncio.run(server_main())