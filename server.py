import socketserver
import threading
import os

class ChatHandler(socketserver.BaseRequestHandler):
    clients = {}
    client_states = {}
    message_files = {}

    def handle(self):
        self.client_name = None
        self.current_chat_partner = None

        while True:
            self.data = self.request.recv(1024).strip().decode("utf-8")
            if not self.client_name:
                if self.data.startswith("Name:"):
                    self.client_name = self.data.split(":")[1]
                    with ChatHandler.lock:
                        ChatHandler.clients[self.client_name] = self.request
                        ChatHandler.client_states[self.client_name] = None
                    self.broadcast(f"{self.client_name} has joined the chat.")
                    self.send_online_users()
                else:
                    self.request.sendall(bytes("Please send your name in the format 'Name: your_name'.\n", "utf-8"))
            else:
                if self.data == "quit":
                    self.request.close()
                    with ChatHandler.lock:
                        del ChatHandler.clients[self.client_name]
                        del ChatHandler.client_states[self.client_name]
                    self.broadcast(f"{self.client_name} has left the chat.")
                    self.send_online_users()
                    break
                elif self.data.startswith("Chat with:"):
                    partner = self.data.split(":")[1].strip()
                    if partner in ChatHandler.clients:
                        self.current_chat_partner = partner
                        ChatHandler.client_states[self.client_name] = f"Chatting with {partner}"
                        self.request.sendall(bytes(f"You are now chatting with {partner}\n", "utf-8"))
                        self.process_message_file()
                    else:
                        self.request.sendall(bytes(f"User {partner} is not online.\n", "utf-8"))
                elif self.data == "End chat":
                    self.current_chat_partner = None
                    ChatHandler.client_states[self.client_name] = None
                    self.request.sendall(bytes("You have ended the current chat\n", "utf-8"))
                    self.process_message_file()
                elif ChatHandler.client_states[self.client_name] and self.current_chat_partner:
                    recipient_name = self.current_chat_partner
                    message = self.data
                    self.send_private_message(recipient_name.strip(), message.strip())
                else:
                    self.request.sendall(bytes("You are not currently in a chat. Use 'Chat with: username' to start a chat.\n", "utf-8"))

    def broadcast(self, message):
        with ChatHandler.lock:
            for client_name, client_socket in ChatHandler.clients.items():
                if client_name != self.client_name:  # Evita enviar mensajes al cliente actual
                    client_socket.sendall(bytes(message + "\n", "utf-8"))

    def send_online_users(self):
        online_users = ", ".join(ChatHandler.clients.keys())
        with ChatHandler.lock:
            for client_name, client_socket in ChatHandler.clients.items():
                client_socket.sendall(bytes(f"Online users: {online_users}\n", "utf-8"))

    def send_private_message(self, recipient_name, message):
        if recipient_name in ChatHandler.clients:
            recipient_socket = ChatHandler.clients[recipient_name]
            recipient_socket.sendall(bytes(f"[Private from {self.client_name}]: {message}\n", "utf-8"))
        else:
            self.store_message(recipient_name, f"[Private from {self.client_name}]: {message}")

    def store_message(self, recipient_name, message):
        file_name = f"{recipient_name}_{self.client_name}.txt"
        with open(file_name, "a") as f:
            f.write(message + "\n")

    def process_message_file(self):
        if self.current_chat_partner:
            file_name = f"{self.client_name}_{self.current_chat_partner}.txt"
            if os.path.exists(file_name):
                with open(file_name, "r") as f:
                    messages = f.readlines()
                for message in messages:
                    self.request.sendall(bytes(message, "utf-8"))
                os.remove(file_name)


HOST, PORT = "localhost", 9888
ChatHandler.lock = threading.Lock()
server = socketserver.ThreadingTCPServer((HOST, PORT), ChatHandler)
try:
    server.serve_forever()
finally:
    server.server_close()
