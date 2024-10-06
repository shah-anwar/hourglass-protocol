import redis, time, random

class RedisClient:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis_conn = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)
        self.redis_conn.flushdb()
        self.key = "available_nodes"

    def save_ip(self, client_ip, client_port):
        timestamp = time.time()
        node_info = f"{client_ip}:{client_port}"
        self.redis_conn.hset(self.key, node_info, timestamp)
        print(f"Saved Node: {node_info} @ {timestamp}")

    def get_random_ips(self, count):
        nodes = self.redis_conn.hkeys(self.key)
        if not nodes:
            return None
        
        random_nodes = random.sample(nodes, min(count, len(nodes)))
        return random_nodes
    
    def remove_expire_nodes(self, expiration_time):
        current_time = time.time()
        nodes = self.redis_conn.hgetall(self.key)

        for node, timestamp in nodes.items():
            if current_time - float(timestamp) > expiration_time:
                self.redis_conn.hdel(self.key, node)