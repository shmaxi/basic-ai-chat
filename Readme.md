# Chat Application

This is a simple chat application that consists of a server and a client. The server can listen to multiple clients simultaneously and broadcast messages from one client to all clients. The client can send and receive messages asynchronously.

## Server

### Requirements

- Python 3.x

### Running the Server

1. Open a terminal window.
2. Navigate to the directory containing the server code (`server.py`).
3. Run the following command to start the server:
```commandline
python server.py
```
The server will start listening for incoming connections from clients.

## Client

### Requirements

- Python 3.x

### Running the Client

1. Open a new terminal window.
2. Navigate to the directory containing the client code (`client.py`).
3. Run the following command to start the client:
```commandline
python client.py
```

By default, the client is set to be controlled by a human. You can use command line arguments to control the client behavior:

- `--is_ai`: Set this flag to make the client controlled by AI.
- `--response_strategy`: Specify the response strategy for AI (timed or count).
- `--ai_message_interval`: Number of messages AI should wait before sending a message.
- `--ai_time_interval`: Number of seconds AI should wait before sending a message.

Please note that running the client with it's AI variant without the OPENAI_API_KEY environment variable will not work and cause the code to exit.
For example, to run the client as an AI with a time-based response strategy and a message interval of 5 messages and a time interval of 3 seconds, use the following command:
```commandline
OPENAI_API_KEY="sk-..." python client.py --is_ai --response_strategy timed --ai_time_interval 3
OPENAI_API_KEY="sk-..." python client.py --is_ai --response_strategy count --ai_message_interval 5
```