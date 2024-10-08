from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend

delim = b"~~" #delimiter

def verify_signature(public_key: rsa.RSAPublicKey, message: bytes, signature: bytes):
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except:
        return False

def process_packet(packet: bytes):
    sections = packet.split(delim)
    command = sections[0].decode('utf-8').strip()
    match command:
        case "JOIN":
            return handle_join(sections)
        case _:
            return None, [None]

def handle_join(sections):
    circuit_id, timestamp, public_key_bytes, signature = sections[1:5]
    reconstructed_data = delim.join(sections[:4])
    
    public_key = serialization.load_pem_public_key(
        public_key_bytes,
        backend=default_backend()
    )
    if not verify_signature(public_key, reconstructed_data, signature):
        return None, [None]
    
    return "JOIN", [circuit_id.hex(), public_key]