import crypto
import asyncio
import socket
import pickle
import os.path
import motor.motor_asyncio
import redis.asyncio as aioredis
from datetime import datetime
from bcrypt import hashpw, gensalt, checkpw
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from getpass import getpass

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
            config_password = getpass("Enter CONFIG password: ")
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
        config_password = getpass("Enter new CONFIG password: ")
        confirm_password = getpass("Confirm password: ")
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
# Client Handling

async def handleClient(reader, writer):
    message = (await reader.readline()).decode().strip()
    request = message.split(":")[0].strip()
    data = message.split(":")[1].strip()
    if request == "CHECK_USERNAME":
        await handleAvailability(data, reader, writer)
    elif request == "REGISTER":
        await handleRegistration(data, reader, writer)
    elif request == "LOGIN":
        await handleLogin(data, reader, writer)

async def handleAvailability(username, reader, writer):
    user_data = await users_collection.find_one({"username": username})
    
    if user_data:
        writer.write(b"USERNAME_TAKEN\n")
    else:
        writer.write(f"PUBLIC_KEY:{public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo).decode()}\n".encode())

async def handleRegistration(encrypted_data, reader, writer):
    try:
        data = private_key.decrypt(
                encrypted_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            ).decode()
    except Exception as e:
        writer.write(b"ERROR: Failed to decrypt message\n")
        await writer.drain()
        writer.close()
        return
    
    username, user_public_key_data = data.split(",", 1)
    existing_user = await users_collection.find_one({"username": username.strip()})
    if existing_user:
        writer.write(b"USERNAME_TAKEN\n")
        await writer.drain()
        writer.close()
        return
    
    user_public_key = serialization.load_pem_public_key(
        user_public_key_data.strip().encode(),
        backend=default_backend()
    )
    
    last_login = None
    await users_collection.insert_one({
        "username": username.strip(),
        "public_key": user_public_key_data.strip(),
        "last_login": last_login
    })

    writer.write(b"REGISTRATION_SUCCESSFUL\n")
    await writer.drain()
    writer.close()
    await writer.wait_closed()

async def handleLogin(message, reader, writer):
    encrypted_username = bytes.fromhex(message)

    try:
        username = private_key.decrypt(
            encrypted_username,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        ).decode()

        print(f"Received and decrypted username: {username}")

        user_data = await loadUser(username)
        user_public_key = user_data["public_key"]
        last_login = user_data["last_login"]
        print(f"Loaded public key for user: {username}")

        challenge = crypto.generateChallenge()
        print(f"Generated challenge: {challenge}")

        writer.write(f"Challenge: {challenge}\n".encode())
        await writer.drain()
        
        signed_challenge_hex = (await reader.readline()).decode().strip()
        signed_challenge = bytes.fromhex(signed_challenge_hex)

        try:
            user_public_key.verify(
                signed_challenge,
                challenge.encode(),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
        except Exception as e:
            print(f"Signature verification failed: {e}")
            writer.write(b"Authentication failed. Signature does not match.\n")
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return

        await updateLastLogin(username)
        print(f"User '{username}' authenticated successfully.")

        writer.write(f"Authentication successful. Last login: {last_login}\n".encode())
        await writer.drain()

        writer.close()
        await writer.wait_closed()

    except Exception as e:
        print(f"Error handling client: {e}")
        writer.write(f"Error: {str(e)}\n".encode())
        await writer.drain()

        writer.close()
        await writer.wait_closed()

# Config Handling

def changeHost():
    global HOST, PORT, private_key, public_key
    while True:
        try:
            HOST = input("Enter HOST: ")
            PORT = int(input("Enter PORT: "))
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((HOST, PORT))
                s.close()  # valid IP and port, close after validation
        except Exception as e:
            print(e)
        else:
            break

async def loadUser(username):
    user_data = await users_collection.find_one({"username": username})

    if user_data is None:
        raise Exception(f"User '{username}' not found in the database.")

    public_key_pem = user_data.get("public_key")
    if not public_key_pem:
        raise Exception(f"No public key found for user '{username}'.")

    user_public_key = serialization.load_pem_public_key(public_key_pem.encode())

    last_login = user_data.get("last_login", "No login data available")

    return {"public_key": user_public_key, "last_login": last_login}

async def updateLastLogin(username):
    await users_collection.update_one(
        {"username": username},
        {"$set": {"last_login": datetime.utcnow()}}
    )

async def startServer():    
    server = await asyncio.start_server(handleClient, HOST, PORT)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')
    
    async with server:
        await server.serve_forever()

async def main():
    if not os.path.isfile('config.pkl'):
        firstRun()
    else:
        configure()
    
    await initRedis()
    await startServer()

if __name__ == '__main__':
    asyncio.run(main())
