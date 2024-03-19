import argparse
from socket import socket as web_socket, AF_INET, SOCK_STREAM
import threading
from queue import Queue

from messaging.message import pack_message, get_unpacked_message


def parse_args():
    parser = argparse.ArgumentParser(description="Server for chat application.")
    parser.add_help = True
    parser.add_argument("--server_ip", type=str, default='127.0.0.1',
                        help="IP address of the server (default: 127.0.0.1)")
    parser.add_argument("--server_port", type=int, default=8888, help="Port number of the server (default: 8888)")
    return parser.parse_args()


class MessageServer:
    def __init__(self, address='127.0.0.1', port=8888):
        self.chat_history = []
        self.clients = []
        self.message_queue = Queue()
        self.address = address
        self.port = port
        self.server_socket = None
        self.broadcast_thread = None

    def start(self):
        # Create a socket object
        self.server_socket = web_socket(AF_INET, SOCK_STREAM)

        try:
            # Bind the socket to a specific IP and port
            self.server_socket.bind((self.address, self.port))

            # Listen for incoming connections
            self.server_socket.listen(5)
            print("Server is listening...")

            # Create a thread to broadcast messages from the queue
            self.broadcast_thread = threading.Thread(target=self.broadcast_messages, args=(self.message_queue, self.clients, self.chat_history))
            self.broadcast_thread.start()

            while self.server_socket is not None:
                # Accept incoming connections from clients
                socket, client_address = self.server_socket.accept()

                # Add the client socket to the list of clients
                self.clients.append(socket)

                # Create a new thread to handle the client
                client_thread = threading.Thread(target=self.handle_client,
                                                 args=(socket, client_address, self.message_queue))
                client_thread.start()
        except Exception as e:
            print(f"Server has stopped working...\n{e}")
            if self.server_socket is not None:
                self.server_socket.close()

    def stop(self):
        if self.server_socket:
            self.server_socket.close()

        self.server_socket = None

    @staticmethod
    def handle_client_message(client_socket, client_address, message_queue):
        message = get_unpacked_message(client_socket)
        if not message:
            return None

        message = MessageServer.get_formatted_message_for_chat(client_address, message)

        # Add the message to the message queue to be broadcast to all the clients asynchronously
        message_queue.put(message)
        return message

    @staticmethod
    def get_formatted_message_for_chat(client_address, message):
        message = f"\nClient <{client_address}> says:\n{message}\n"
        return message

    # Function to handle client connections
    @staticmethod
    def handle_client(client_socket, client_address, message_queue):
        print(f"Accepted connection from {client_address}")

        while True:
            try:
                message = MessageServer.handle_client_message(client_socket, client_address, message_queue)
                if not message:
                    break

            except Exception as e:
                print(f"Client socket of address {client_address} has crashed. Closing socket.")

        # Close the client socket
        client_socket.close()
        print(f"Connection from {client_address} closed")

    # Function to broadcast messages from the queue to all clients
    @staticmethod
    def broadcast_messages(message_queue, clients, chat_history):
        while True:
            MessageServer.handle_messages_from_queue(clients, message_queue, chat_history)

    @staticmethod
    def handle_messages_from_queue(clients, message_queue, chat_history):
        message = message_queue.get()
        chat_history.append(message)
        message_with_header = pack_message(message)
        print(f"Brodcasting message to all clients:\n {message}\n____________________")
        MessageServer.broadcast_message_to_clients(clients, message_with_header)

    @staticmethod
    def broadcast_message_to_clients(clients, message_with_header):
        for client in clients:
            try:
                # Send the message with header to all clients
                client.send(message_with_header)
            except Exception as e:
                print(f"Error broadcasting message to {client}: {e}")
                client.close()
                clients.remove(client)


if __name__ == '__main__':
    # Parse command line arguments
    args = parse_args()
    server = MessageServer(
        address=args.server_ip,
        port=args.server_port
    )
    server.start()
