import socket, multiprocessing
from .packet_builder import PacketBuilder
from .api.api_manager import APIManager

def client_process(pipe):
    while True:
        msg = pipe.recv()
        break
        #pass

class Client:
    def __init__(self, host='127.0.0.1', port=123):
        pass