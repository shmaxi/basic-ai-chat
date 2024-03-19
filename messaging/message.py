import struct


# pack_message packs the received message with a 4-byte integer header, representing the message length
def pack_message(message):
    # Pack the message length as a 4-byte integer
    message_length = len(message)
    message_header = struct.pack("!I", message_length)
    # Add the message header to the message
    message_with_header = message_header + message.encode()
    return message_with_header


# get_unpacked_message handles the receiving of messages and their correct unpacking and decoding
def get_unpacked_message(socket):
    # Receive the message header (4 bytes)
    header_bytes = socket.recv(4)
    if not header_bytes:
        return None

    # Unpack the message length from the header
    message_length = struct.unpack("!I", header_bytes)[0]

    # Receive the entire message based on the message length
    message = socket.recv(message_length).decode()
    return message
