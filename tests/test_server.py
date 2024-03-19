# Unit tests for server code
import socket
import threading
import unittest
from queue import Queue

from messaging.message import get_unpacked_message, pack_message
from server import MessageServer


class TestServer(unittest.TestCase):
    def setUp(self):
        # Create a socket object
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to a specific IP and port
        self.server_socket.bind(('127.0.0.1', 8888))

        # Listen for incoming connections
        self.server_socket.listen(5)

        # Create a message queue
        self.message_queue = Queue()

    def tearDown(self):
        # Close server socket
        self.server_socket.close()

    def test_message_broadcast(self):
        clients = []
        client_connections = []

        # Mock client connections
        for _ in range(3):
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('127.0.0.1', 8888))
            client_connection, client_addr = self.server_socket.accept()
            client_connections.append(client_connection)
            clients.append(client_socket)

        # Test broadcasting a message
        test_message = "Hello, world!"

        # Send the message with header to the message queue
        self.message_queue.put(test_message)

        # Start broadcasting thread
        broadcast_thread = threading.Thread(target=MessageServer.handle_messages_from_queue, args=(client_connections, self.message_queue))
        broadcast_thread.start()

        # Check if all clients received the message
        for client_socket in clients:
            received_message = get_unpacked_message(client_socket)
            self.assertEqual(received_message, test_message)

        for client_connection in client_connections:
            client_connection.close()

        # Close client sockets
        for client_socket in clients:
            client_socket.close()

    def test_handle_client_message(self):
        # Mock client connection
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', 8888))

        # Send a message with header to the server
        test_message = "Test message"
        packed_message = pack_message(test_message)
        client_socket.send(packed_message)

        # Accept the client connection and handle it
        client_sock, client_addr = self.server_socket.accept()
        MessageServer.handle_client_message(client_sock, client_addr, self.message_queue)

        # Check if the message was added to the message queue
        received_message = self.message_queue.get()
        expected_message = f"\nClient <{client_addr}> says:\n{test_message}\n"
        self.assertEqual(received_message, expected_message)

        # Close client socket
        client_socket.close()

        # Close the incoming client socket for the server
        client_sock.close()


if __name__ == '__main__':
    unittest.main()