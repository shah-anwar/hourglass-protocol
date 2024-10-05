# takes in packets and decides if sent to circuit handler (sending messages as self, or redirecting as an internal node)
# or send packets directly to server as the exit node of a circuit
from .circuit_handler import CircuitHandler
from .exit_node_handler import ExitNodeHandler
from .origin_node_handler import OriginNodeHandler

import random, asyncio, socket

class APIManager:
    def __init__(self, server, server_port):
        self.circuits = {"circuit_id": CircuitHandler("circuit_id", "ip address", "ip address")} #format
        self.exits = {"circuit_id": ExitNodeHandler("circuit_id", "ip address", "ip address")} #receives data from both server and random other circuits
        self.origin = None

        self.server = server
        self.server_port = server_port

        #{"circuit_id": OriginNodeHandler("circuit_id", "ip address")}

    def send_message(self, message, destination):
        pass

    def exit_message(self, message):
        pass

    def new_origin(self, circuit_id, message):
        ip_list = self.get_ips()
        return ip_list
        #chosen_node = random.choice(ip_list)
        #self.origin = OriginNodeHandler(circuit_id, chosen_node)

    def get_ips(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.server, self.server_port))
            message = "LOGIN"
            s.sendall(message.encode())
            print("Msg Sent")

            response = s.recv(1024)
            return response

    def process_message(self, message):
        # find recipient
        # extract circuit id
        # match id to dictionary of circuits and exits
        # send message to required handler
        match message:
            case "JOIN":
                pass
            
    def get_purpose(self, message):
        return True
    