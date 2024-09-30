import threading, socket, pickle, sys, selectors, types, os.path

sel = selectors.DefaultSelector()

def firstRun():
    global HOST, PORT
    changeHost()
    with open('config.pkl', 'w') as f:
        pickle.dump([HOST, PORT, ])

def configure():
    pass

def changeHost():
    while True:
        try:
            HOST = input("Enter HOST: ")
            PORT = int(input("Enter PORT: "))
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((HOST, PORT))
                s.listen()
                conn, addr = s.accept()
                with conn:
                    print(f"Connected by {addr}")
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        conn.sendall(data)
        except Exception as e:
            print(e)
        else:
            break

def main():
    if not os.path.isfile('config.pkl'):
        firstRun()
    else:
        configure()

if __name__ == '__main__':
    main()