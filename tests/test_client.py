# Unit tests for client code
import socket
import unittest
from queue import Queue

from client import MessageClient
from messaging.message import pack_message
from server import MessageServer


class TestClient(unittest.TestCase):
    def setUp(self):
        # Create a socket object
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to a specific IP and port
        self.server_socket.bind(('127.0.0.1', 9999))

        # Listen for incoming connections
        self.server_socket.listen(5)

        # Create a message queue
        self.message_queue = Queue()

    def tearDown(self):
        # Close server socket
        self.server_socket.close()
        self.server_socket = None

    def test_handle_message(self):
        # Create a socket object
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Mock server connection
        client_socket.connect(('127.0.0.1', 9999))

        # Mock receiving a message
        test_message = "Test message"

        # Accept the client connection and handle it
        client_sock_for_server, client_addr = self.server_socket.accept()
        formatted_message = MessageServer.get_formatted_message_for_chat(client_addr, test_message)
        packed_message = pack_message(formatted_message)

        message_client = MessageClient()
        client_sock_for_server.send(packed_message)

        # Test receiving the message
        message_client.handle_message(client_socket)

        is_message_received = False
        for message in message_client.chat_history:
            if message == formatted_message:
                is_message_received = True

        self.assertTrue(is_message_received)

        # Close client socket
        client_socket.close()


if __name__ == "__main__":
    unittest.main()
