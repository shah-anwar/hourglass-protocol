import crypto
import asyncio, socket, pickle, os.path
import motor.motor_asyncio
import redis.asyncio as aioredis
from bcrypt import hashpw, gensalt, checkpw

from cryptography.hazmat.primitives.asymmetric import rsa

### MongoDB connection

client = motor.motor_asyncio.AsyncIOMotorClient('mongodb')
db = client.hourglass_db
users_collection = db.users

### Redis for session management and logging
redis = None

USER_SESSION_KEY = "user_session:{}"
LOG_KEY = "hourglass_db"

async def initRedis():
    global redis
    redis = await aioredis.from_url("redis://localhost")
    
async def logEvent(event):
    await redis.lpush(LOG_KEY, event)

### Config Stuff

def configure():
    global HOST, PORT, private_key, public_key
    print("Reading from config file...")
    with open('config.pkl', 'rb') as f:
        HOST, PORT, encrypted_key = pickle.load(f)
    
    while True:
        try:
            config_password = input("Enter CONFIG password: ")
            private_key = crypto.decryptKey(encrypted_key, config_password)
        except Exception as e:
            print(f"Decryption failed: {e}")
            print("Password incorrect! Please try again.")
        else:
            break
        
    public_key = private_key.public_key()
    print("Config loaded successfully.")

def firstRun():
    global HOST, PORT, private_key, public_key
    changeHost(HOST, PORT, private_key, public_key)

    print("Generating Keys...")
    private_key, public_key = crypto.generateKeys()
    
    print(f"Keys generated.")
    print("")
    
    while True:
        config_password = input("Enter new CONFIG password: ")
        confirm_password = input("Confirm password: ")
        if config_password == confirm_password:
            print("Password accepted.\n")
            break
        else:
            print("Passwords don't match! Please try again.\n")
            
    print("Writing to config file...")
    
    encrypted_key = crypto.encryptKey(crypto.getKeyAsBytes(private_key), config_password)
    
    with open('config.pkl', 'wb') as f:
        pickle.dump([HOST, PORT, encrypted_key], f)

### Server Stuff

async def handleClient(reader, writer):
    try:
        writer.write(b"Welcome to the Hourglass Protocol. Please log in.\n")
        await writer.drain()

        writer.write(b"Username: ")
        await writer.drain()
        username = (await reader.readline()).decode().strip()

        writer.write(b"Password: ")
        await writer.drain()
        password = (await reader.readline()).decode().strip()

        print(f"Received credentials - Username: {username}, Password: {password}")

        # Perform user authentication here

        # If login is successful, send a confirmation to the client
        writer.write(b"Login successful.\n")
        await writer.drain()

    except (BrokenPipeError, ConnectionResetError, asyncio.IncompleteReadError) as e:
        print(f"Connection error: {e}")
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception as e:
            print(f"Error closing the writer: {e}")

def changeHost():
    global HOST, PORT, private_key, public_key
    while True:
        try:
            HOST = input("Enter HOST: ")
            PORT = int(input("Enter PORT: "))
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((HOST, PORT))
                s.close() # valid ip and port, close after validation
        except Exception as e:
            print(e)
        else:
            break

async def startServer():    
    server = await asyncio.start_server(handleClient, HOST, PORT)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')
    
    async with server:
        await server.serve_forever()

### Main

async def main():
    if not os.path.isfile('config.pkl'):
        firstRun()
    else:
        configure()
    
    await initRedis()
    await startServer()

if __name__ == '__main__':
    asyncio.run(main())