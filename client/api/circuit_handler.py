import asyncio
from .packet_handler import process_packet

from cryptography.hazmat.primitives.asymmetric import rsa

# redirects packets to next node in the circuit

"""
Directionality:

Origin -> Back_Node -> (YOU) -> Front_Node -> Exit -----------> Server [forward moving message]
Origin <- Back_Node <- (YOU) <- Front_Node <- Exit <----------- Server [backward moving message]

"""

class CircuitHandler:
    def __init__(self, circuit_id: bytes, ip_list, back_node, forwards_private_key: rsa.RSAPrivateKey, back_public_key: rsa.RSAPublicKey):
        self.circuit_id = circuit_id
        self.ip_list = ip_list
        self.back_node_reader, self.back_node_writer = back_node #in form (reader, writer)
        
        self.forwards_private_key = forwards_private_key #private key to decrypt messages arriving forwards
        self.back_public_key = back_public_key #public key to encrypt messages sending backwards

        self.front_node = self.initialise_front_node()
    
    def initialise_front_node(self):
        pass
    
    #forwards messages

    async def send_forward(self):
        #send a message forwards in the circuit (to the front_node)
        pass

    async def receive_backward_message(self):
        #receive a message from front_node
        pass
    
    #backwards messages

    async def send_backward(self):
        #send a message backwards in the circuit (to the back_node)
        pass

    async def receive_forward_message(self):
        #receive a message from back_node
        try:
            data = await self.back_node_reader.read(1024)
            if not data:
                print("No data from BackNode. Closing connection.")
            
            packet = data.decode().strip()
            print("Received packet from BackNode")

            header, result = process_packet(packet)
            #result in form "REDIRECT", timestamp, payload (for origin), signature 

        except Exception as e:
            print(f"Error while handling BackNode: {e}")

        finally:
            print("Closing connection with BackNode")
            self.back_node_writer.close()
            await self.back_node_writer.closed()
