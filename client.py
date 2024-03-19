import argparse
import os
import socket
import threading
import time

from openai import OpenAI

from messaging.message import get_unpacked_message, pack_message


# Function to parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Client for chat application.")
    parser.add_help = True
    parser.add_argument("--server_ip", type=str, default='127.0.0.1',
                        help="IP address of the server (default: 127.0.0.1)")
    parser.add_argument("--server_port", type=int, default=8888, help="Port number of the server (default: 8888)")
    parser.add_argument("--is_ai", action="store_true", default=False,
                        help="Whether the client should be controlled by AI (default: False). If selected, "
                             "the OPENAI_API_KEY environment variable is required.")
    parser.add_argument("--response_strategy", choices=["timed", "count"], default="timed",
                        help="Response strategy for AI (default: timed)")
    parser.add_argument("--ai_message_interval", type=int, default=5,
                        help="Number of messages the AI should wait before sending a message (default: 5)")
    parser.add_argument("--ai_time_interval", type=int, default=3,
                        help="Number of seconds the AI should wait before sending a message (default: 3)")
    return parser.parse_args()


def get_message_from_open_ai(chat_history):
    open_ai_client = OpenAI()

    existing_chat_messages = [
        {
            "role": "user",
            "content": message
        }
        for message in chat_history
    ]

    completion = open_ai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a friendly participant in a group chat, trying to make friends."
            },
            *existing_chat_messages
        ]
    )

    return completion.choices[0].message.content


class MessageClient:
    def __init__(self, address='127.0.0.1', port=8888, ai_message_interval=None, ai_time_interval=None):
        self.address = address
        self.port = port
        self.client_socket = None
        self.ai_message_interval = ai_message_interval
        self.ai_time_interval = ai_time_interval
        self.chat_history = []

    def start(self, is_ai=False, response_strategy='timed'):
        """
        start makes the MessageClient listen to incoming chat broadcasts and allows the client to send messages
        :param is_ai: Signifies whether the client is human controlled or controlled by AI
        :param response_strategy: Signifies whether the AI responds every N seconds or every N messages. Valid values are ('timed', 'count'). Is taken into account only if is_ai parameter is True.
        :return:
        """
        # Create a socket object
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Connect to the server
            self.client_socket.connect((self.address, self.port))

            # Create a thread to receive messages from the server
            receive_thread = threading.Thread(target=self.receive_messages, args=(self.client_socket,))
            receive_thread.start()

            if is_ai:
                self.handle_ai_client(response_strategy)
            else:
                self.handle_human_client()
        except Exception as e:
            print(f"Client has stopped working...\n{e}")
            if self.client_socket is not None:
                self.client_socket.close()

    def stop(self):
        if self.client_socket:
            self.client_socket.close()

        self.client_socket = None

    def receive_messages(self, client_socket):
        while True:
            try:
                self.handle_message(client_socket)
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def handle_message(self, client_socket):
        message = get_unpacked_message(client_socket)
        self.chat_history.append(message)
        formatted_message = f"\n> {message}\n>"
        print(formatted_message)

    @staticmethod
    def send_message(client_socket, message):
        packed_message = pack_message(message)
        client_socket.send(packed_message)

    def handle_human_client(self):
        print("Enter your messages:\n> ")
        while True:
            # Get user input
            message = input()

            # Send the message to the server with header
            self.send_message(self.client_socket, message)

    def handle_ai_client(self, response_strategy):
        if response_strategy == 'timed':
            self.handle_timed_ai_client()
        elif response_strategy == 'count':
            self.handle_count_ai_client()
        else:
            raise Exception(f'Unknown response_strategy: {response_strategy}')

    def handle_count_ai_client(self):
        if not self.ai_message_interval:
            raise ValueError(f'Undefined ai_message_interval')
        while True:
            if len(self.chat_history) % self.ai_message_interval == 0:
                message = get_message_from_open_ai(self.chat_history)
                self.client_socket.send(pack_message(message))
                time.sleep(0.5)  # Sleep for half a second just so that we are able to get the conversation update
                # from the server prior to the generation of another message

    def handle_timed_ai_client(self):
        if not self.ai_time_interval:
            raise ValueError(f'Undefined ai_time_interval')
        while True:
            message = get_message_from_open_ai(self.chat_history)
            self.client_socket.send(pack_message(message))
            time.sleep(self.ai_time_interval)


if __name__ == '__main__':
    # Parse command line arguments
    args = parse_args()

    # Check if is_ai is set and OPENAI_API_KEY is available
    if args.is_ai and not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable is not set.")
        exit(1)

    client = MessageClient(
        address=args.server_ip,
        port=args.server_port,
        ai_message_interval=args.ai_message_interval,
        ai_time_interval=args.ai_time_interval
    )
    client.start(is_ai=args.is_ai, response_strategy=args.response_strategy)
