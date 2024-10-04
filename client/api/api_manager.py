# takes in packets and decides if sent to circuit handler (sending messages as self, or redirecting as an internal node)
# or send packets directly to server as the exit node of a circuit
from .circuit_handler import CircuitHandler
from .exit_node_handler import ExitNodeHandler

class APIManager:
    def __init__(self):
        self.circuits = {"circuit_id": CircuitHandler("circuit_id", "ip address", "ip address")} #format
        self.exits = {"circuit_id": ExitNodeHandler("circuit_id", "ip address", "ip address")} #receives data from both server and random other circuits
    
    def process_message(self, message):
        # find recipient
        # extract circuit id
        # match id to dictionary of circuits and exits
        # send message to required handler
        if (self.get_purpose(message)):
            CircuitHandler.handle_circuit_message(message)
        else:
            ExitNodeHandler.handle_exit_message(message)
            
    def get_purpose(self, message):
        return True
    