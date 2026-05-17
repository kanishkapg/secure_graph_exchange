import struct
import socket

def send_message(sock, data_bytes):
    """
    Sends a message over a socket securely by prefixing it with its length.
    Ensures complete payloads are delivered.
    """
    # Pack the length of the data into 4 bytes
    length_prefix = struct.pack('>I', len(data_bytes))
    sock.sendall(length_prefix + data_bytes)

def receive_message(sock):
    """
    Receives a complete message from a socket using the length prefix.
    """
    # Read the 4-byte length prefix first
    length_bytes = recv_all(sock, 4)
    if not length_bytes:
        return None
    msg_len = struct.unpack('>I', length_bytes)[0]
    
    # Read the exact length of the message
    return recv_all(sock, msg_len)

def recv_all(sock, n):
    """Helper function to receive exactly n bytes."""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return bytes(data)