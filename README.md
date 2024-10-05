
# ⧗ Hourglass Protocol ⧖

This project aims to develop a distributed client-node communication system where users communicate with each other through multi-node circuits. The core client program establishes connections to nodes, which form circuits allowing users to interact without revealing their actual IP addresses. The client manages all network-level communication, routing, and encryption, while a separate GUI application provides an interface for user interaction. The system is designed to handle large-scale, secure communication, integrating cryptography, Redis and MongoDB databases, and a modular architecture that separates backend logic from frontend presentation.

Users communicate with each other by utilizing circuits composed of multiple intermediary nodes. Instead of direct connections, users send messages through their exit node, which connects to the recipient's exit node, ensuring anonymity for both parties.

The project also implements Zero-Knowledge Proofs (ZKP) and encrypted heartbeats to verify that users are actively contributing to the network as nodes without revealing their IP addresses.

## Key Features:

1. **Circuit-Based User Communication**: Users communicate with each other using circuits formed by routing messages through a series of intermediary nodes. A user’s outgoing message is forwarded from node to node until it reaches their exit node, which then connects to the recipient’s exit node. This ensures that neither user’s real IP address is exposed to the other, providing full anonymity.
        Communication Flow:
            User A sends a message to their nearest node.
            The message travels through a series of nodes, forming a circuit.
            The last node in User A’s circuit, the exit node, forwards the message to User B's exit node.
            The message is then delivered to User B without User A knowing User B’s IP address or vice versa.

2. **Separation of Client and GUI**: The client program operates independently from the GUI, handling all networking, cryptography, and routing. The client provides an API that the GUI interacts with, allowing the user to view connection statuses, send requests, and receive data without managing the underlying complexity.

3. **Node Management**: The client autonomously manages connections to multiple nodes, facilitating secure communication between users through node-based circuits. The server provides node discovery but never directly interacts with the user or GUI.

4. **GUI for User Interaction**: A standalone GUI application, built with a framework like Tkinter or PyQt, interacts with the backend client via API. The GUI allows users to view real-time data such as connection statuses, send messages through circuits, and manage their connections to nodes.

5. **Inter-Process Communication (IPC) via API**: The client program exposes an API that the GUI uses to communicate with the backend. This separation ensures that the client can manage complex operations like cryptographic packet handling and message routing while providing a simple interface for the user to interact with.

6. **Packet Handling and Cryptography**: The client program handles all aspects of packet management, including encryption, decryption, and routing through circuits. Cryptography (using libraries like cryptography) is employed to ensure that data remains secure at every hop in the circuit. Messages are encrypted and decrypted as they pass through nodes, with each node only knowing the next-hop node's IP.

7. **Database Integration**: The system integrates with Redis and MongoDB to manage both short-term and long-term data:
        Redis: Used for fast, in-memory storage of active circuits, routing data, and message queues.
        MongoDB: Provides long-term storage for logs, user profiles, communication histories, and node information.

8. **User-to-User Communication via Circuits and Exit Nodes**:
        Circuit-Based Routing: Users never connect directly to each other. Instead, a multi-hop circuit is established between the sender's exit node and the recipient’s exit node. The exit nodes serve as the final intermediary between two users, ensuring that neither party learns the other's true IP address.
        Exit Node Connection: User A’s exit node forwards the message to User B’s exit node, which delivers it to User B. This process maintains user privacy and anonymizes the connection.

9. **Zero-Knowledge Proofs (ZKP) and Heartbeats for Node Verification**: To maintain the integrity of the network, users are required to prove they are participating as nodes within the system, without revealing their actual IP addresses. This is accomplished using Zero-Knowledge Proofs (ZKP) and encrypted heartbeats:
        ZKP for Node Proof: Users provide a cryptographic proof that demonstrates they are acting as a node, actively routing messages for other users. This proof allows the network to verify a user’s contribution without revealing their identity or IP address.
        Heartbeats for Node Activity: Encrypted heartbeats are sent periodically from each node to verify continued participation. These heartbeats ensure that nodes remain active and available for routing, and are cryptographically signed to prevent tampering.

10. **Anonymity Through Circuit-Based Communication**:
        Message Routing: Messages between users are routed through multiple nodes using encrypted channels. Each user’s exit node delivers the message to the recipient’s exit node, maintaining the anonymity of both the sender and recipient.
        No IP Address Disclosure: Users never reveal their real IP addresses to each other or the server. The server knows only the exit node IPs involved in the connection, preserving the anonymity of the communication process.

## Technology Stack

**Python**: Core language for implementing client, server, and API logic.

**ZeroMQ (or Raw Socket Programming)**: Handles network communication and message routing between nodes, allowing low-level control over connections.

**Redis**: High-performance in-memory data store used for caching and managing real-time data like message queues and routing tables.

**MongoDB**: NoSQL database for permanent storage of logs, communication histories, and node data.

**Tkinter / PyQt**: GUI frameworks for building the user-facing application that communicates with the backend.

**Cryptography Library**: Used to implement encryption, decryption, and secure key exchange between users and nodes.

## System Architecture

**Client Backend**: The client backend manages communication with nodes and servers, establishes circuits, and routes messages through nodes. It ensures all data is encrypted and transmitted securely across the network. Redis and MongoDB are used to manage fast caching and long-term storage, respectively.

**API for Frontend**: The backend client exposes a simple API that the GUI can interact with, allowing the user to manage connections, send messages, and receive updates about circuit statuses without being directly involved in the network logic.

**GUI Frontend**: The GUI application allows users to interact with the backend client in a user-friendly way. It provides real-time status updates on connections and routes, and enables the user to send messages through their exit node to other users.

**Circuits for Message Routing**: The system routes user messages through a series of nodes, forming a circuit. Users’ exit nodes handle the final delivery of messages, ensuring that IP addresses remain hidden. Each circuit provides multiple layers of encryption to ensure secure communication.

**ZKP and Heartbeat System**: Users must prove they are acting as nodes in the network by using Zero-Knowledge Proofs (ZKP). Periodic encrypted heartbeats ensure that all nodes are active and contributing to the network, while maintaining user privacy.

## Use Cases

**Anonymized User Communication**: Users can communicate securely and privately using node-based circuits without ever exposing their IP addresses.

**Distributed Node Verification**: The system uses ZKP and heartbeats to verify that all users are contributing as nodes while preserving their anonymity.

**User-Friendly GUI**: The GUI allows users to interact with the network, send messages, and monitor connections without needing to manage the underlying complexity of routing and encryption.

## Sequence Diagrams
![Getting IPs](https://github.com/shah-anwar/hourglass-protocol/blob/alternate/reference/1.png?raw=true)
