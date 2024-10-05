class PacketHandler:
    def handle_packet(self, packet):
        if packet.startswith("REGISTER"):
            return "Welcome to the circuit!"
        elif packet.startswith("LOGIN"):
            return "test ip"
        else:
            return "Unknown command"