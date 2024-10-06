delim = b"~~"

from redis_client import RedisClient
redis_db = RedisClient()

class PacketHandler:
    def process_packet(self, data: bytes, address):
        sections = data.split(delim)
        command = sections[0].decode('utf-8').strip()
        match command:
            case "GETIPS":
                return self.handle_get_ips(sections, address)

    def handle_get_ips(self, sections, address) -> bytes:
        count = int(sections[1])
        client_ip, client_port = address
        
        available_ips = redis_db.get_random_ips(count)
        if available_ips is None:
            response = b"DATABASE_EMPTY"
        else:
            response = "~~".join(available_ips)
            response = response.encode()

        redis_db.save_ip(client_ip, client_port)

        return response