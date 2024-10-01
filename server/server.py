import asyncio, socket, pickle, os.path
from cryptography.hazmat.primitives.asymmetric import rsa

def configure():
    global HOST, PORT, private_key, public_key
    print("Reading from config file...")
    with open('config.pkl') as f:
        HOST, PORT, private_key = pickle.load(f)
    print("Variables loaded successfully.")

def firstRun():
    global HOST, PORT, private_key, public_key
    changeHost()

    print("Generating Keys...")
    private_key, public_key = generateKeys()
    
    print(f"Keys generated.")
    print("")
    print("Writing to config file...")
    
    with open('config.pkl', 'w') as f:
        pickle.dump([HOST, PORT, private_key], f)

def generateKeys():
    private_key = rsa.generate_private_key(65537, 2048)
    return private_key, private_key.public_key()

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Connected with {addr}")

    while True:
        data = await reader.read(1024)
        if not data:
            print(f"Connection with {addr} closed.")
            break
        msg = data.decode()
        print(f"{msg} received from: {addr}")

        response = f"Echo {msg}"
        writer.write(response.encode())
        await writer.drain()

    writer.close()
    await writer.wait_closed()

def changeHost():
    global HOST, PORT, private_key, public_key
    while True:
        try:
            HOST = input("Enter HOST: ")
            PORT = int(input("Enter PORT: "))
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((HOST, PORT))
                s.close() #valid ip and port, close after validation
        except Exception as e:
            print(e)
        else:
            break

async def startServer():
    server = await asyncio.start_server(handle_client, HOST, PORT)

def main():
    if not os.path.isfile('config.pkl'):
        firstRun()
    else:
        configure()
    
    startServer() 

if __name__ == '__main__':
    main()