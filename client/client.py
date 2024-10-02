import asyncio
import os
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa

from getpass import getpass

# get filepath and username, return private key
def loadPrivateKey(filepath, username):
    password = getpass(f"Enter password for {username}: ").encode()
    try:
        with open(filepath, "rb") as key_file:
            private_key = serialization.load_pem_private_key(key_file.read(), password=password, backend=default_backend())
        return private_key
    except Exception as e:
        print(f"Error loading private key: {e}")
        return None

# load the server's private key from the servers directory
def loadServerPublicKey(server):
    server_dir = os.path.join(os.path.dirname(__file__), 'servers/')
    serverPemFile = os.path.join(server_dir, f"{server}.pem")
    
    if not os.path.exists(serverPemFile):
        print(f"Error: Public key for server '{server}' not found in 'servers/' directory.")
        return None
    
    try:
        with open(serverPemFile, "rb") as key_file:
            public_key = serialization.load_pem_public_key(key_file.read(), backend=default_backend())
        return public_key
    except Exception as e:
        print(f"Error loading server public key: {e}")
        return None

# list PEM files in the 'users/' directory and allow the user to select one
def selectUser():
    userDir = os.path.join(os.path.dirname(__file__), 'users/')
    pemFiles = [f for f in os.listdir(userDir) if f.endswith('.pem')]
    
    if not pemFiles:
        print("No PEM files found in the 'users/' directory.")
        return None, None, None
    
    print("Available Users:")
    for i, pemFile in enumerate(pemFiles):
        username, server = pemFile.split("@")
        print(f"{i + 1}. {username} @ {server}")
    
    selection = int(input("Select a file by number: ")) - 1
    if selection < 0 or selection >= len(pemFiles):
        print("Invalid selection.")
        return None, None, None
    
    pemFile = pemFiles[selection]
    filepath = os.path.join(userDir, pemFile)
    
    # extract username and server address from the file name
    username, server_address = pemFile.split("@")
    server_address = server_address.replace(".pem", "")
    
    return filepath, username, server_address

async def register():
    while True:
        username = input("Choose a username: ")
        server_address = input("Enter the server address: ")
        
        # check if the username is available
        try:
            reader, writer = await asyncio.open_connection(server_address, 123)
            writer.write(f"CHECK_USERNAME:{username}\n".encode())
            await writer.drain()
            
            response = (await reader.readline()).decode().strip()
            if response == "USERNAME_TAKEN":
                print("Username is taken. Please choose another.")
                continue  # prompt the user to re-enter username
            elif response.startswith("PUBLIC_KEY:"):
                server_public_key_data = response.split(":")[1].strip()
                server_public_key = serialization.load_pem_public_key(
                    server_public_key_data.encode()
                )

                with open(f"servers/{server_address}.pem", "wb") as key_file:
                    key_file.write(server_public_key_data.encode())
                
                print("Server public key saved.")

                user_private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048,
                )
                user_public_key = user_private_key.public_key()

                user_public_key_pem = user_public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                
                while True:
                    password = getpass("Set a password for your private key: ")
                    confirm_password = getpass("Confirm your password: ")
                    
                    if password != confirm_password:
                        print("Passwords do not match. Please try again.")
                    else:
                        break
                
                encrypted_private_key = user_private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                )

                with open(f"users/{username}@{server_address}.pem", "wb") as key_file:
                    key_file.write(encrypted_private_key)
                
                print("User's public key saved.")

                registration_message = f"{username}, {user_public_key_pem.decode()}"
                encrypted_message = server_public_key.encrypt(
                    registration_message.encode(),
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                encrypted_message = b"REGISTER:" + encrypted_message

                writer.write(encrypted_message + b'\n')
                await writer.drain()

                server_response = (await reader.readline()).decode().strip()
                print(server_response)  # confirmation message

                writer.close()
                await writer.wait_closed()

                print("You can now log in.")
                await login()
                break
        except Exception as e:
            print(f"Error: {e}")

async def login():
    filepath, username, server_address = selectUser()
    try:
        user_private_key = loadPrivateKey(filepath, username)
        server_public_key = loadServerPublicKey(server_address)
        reader, writer = await asyncio.open_connection(server_address, 123)

        encrypted_username = server_public_key.encrypt(
            username.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        writer.write(b"LOGIN:" + encrypted_username.hex().encode() + b'\n')
        await writer.drain()

        challenge = (await reader.readline()).decode().strip().replace("Challenge: ", "")
        print(f"Received challenge: {challenge}")

        signed_challenge = user_private_key.sign(
            challenge.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        encrypted_challenge = server_public_key.encrypt(
                            signed_challenge.encode(),
                            padding.OAEP(
                                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                algorithm=hashes.SHA256(),
                                label=None
                            )
                        )

        writer.write(encrypted_challenge.hex().encode() + b'\n')
        await writer.drain()

        server_response = (await reader.readline()).decode().strip()
        print(server_response)

        writer.close()
        await writer.wait_closed()

    except Exception as e:
        print(f"Error: {e}")

async def clientMain():
    action = input("Do you want to (L)ogin or (R)egister? ").strip().lower()
    
    if action == 'r':
        await register()
    elif action == 'l':
        await login()
    else:
        print("Invalid option. Please select 'L' to login or 'R' to register.")

if __name__ == "__main__":
    asyncio.run(clientMain())