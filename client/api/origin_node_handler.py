# for messages the user sends, and is directed to the user

import random, time, asyncio
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asymmetric_padding
from .packet_builder import PacketBuilder

packet_builder = PacketBuilder()

class OriginNodeHandler:
    def __init__(self, circuit_id: bytes, ip_list):
        self.circuit_id = circuit_id
        self.ip_list = ip_list
        self.forwards_private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        self.max_wait_time = 60
        self.request_interval = 20

        asyncio.create_task(self.request_random_node())
    
    def handle_circuit_message(self, message: bytes):
        pass

    def send_forward():
        pass
    
    def send_backward():
        pass
    
    def get_direction():
        pass

    async def request_random_node(self):
        start_time = time.time()

        while self.ip_list:
            current_time = time.time()
            elapsed_time = current_time - start_time

            if elapsed_time > self.max_wait_time:
                print("Timeout: No response received within 1 minute")
                break
            
            chosen_node = random.choice(self.ip_list)
            message = packet_builder.join_request(self.circuit_id, self.forwards_private_key)
            success = await self.send_request(chosen_node, message)    

            if not success:
                print(f"Resquest to {chosen_node} failed. Removing from list.")
                self.ip_list.remove(chosen_node)

            await asyncio.sleep(30)
        
        print(chosen_node)

    async def send_request(self, chosen_node: str, message: bytes):
        try:
            ip, port = chosen_node.split(":")
            print(f"Attempting connection to {ip}")

            reader, writer = await asyncio.open_connection(ip, int(port))
            writer.write(message)
            await writer.drain()

            response_task = asyncio.create_task(self.receive_response(reader))

            done, pending = await asyncio.wait(
                [response_task],
                timeout=self.max_wait_time,
                return_when=asyncio.FIRST_COMPLETED
            )

            for task in pending:
                task.cancel()
            
            if response_task in done:
                response_received = response_task.result()
                if response_received:
                    print(f"Response received from {ip}")
                    return True
                else:
                    print(f"No response from {ip}")
                    return False
            else:
                print(f"Timeout: No response from {ip}")

        except Exception as e:
            print(f"Error sending request to {ip}")
            return False
        
        finally:
            if writer:
                writer.close()
                await writer.wait_closed()
        
    async def receive_response(self, reader: asyncio.StreamReader):
        try:
            response = await reader.read(1024)
            if response:
                return response.decode()
            else:
                return None
        except Exception as e:
            print(f"Error receiving response: {e}")
            return None


