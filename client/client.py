import asyncio

# Example client code
async def main():
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    reader, writer = await asyncio.open_connection('127.0.0.1', 123)

    # Wait for welcome message from the server
    welcome_msg = await reader.readline()
    print(welcome_msg.decode().strip())

    # Send Username
    writer.write(f"{username}\n".encode())
    await writer.drain()

    # Send Password
    writer.write(f"{password}\n".encode())
    await writer.drain()

    # Wait for response from the server
    login_response = await reader.readline()
    print(login_response.decode().strip())

    # Close the connection
    writer.close()
    await writer.wait_closed()

# Run the client
if __name__ == "__main__":
    asyncio.run(main())
