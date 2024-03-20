import socketserver
import threading

class ChatHandler(socketserver.BaseRequestHandler):
    clients = {}
    lock = threading.Lock()
    message_buffer = {}

    def handle(self):
        self.client_name = None
        self.current_chat_partner = None

        while True:
            self.data = self.request.recv(1024).strip().decode("utf-8")
            if not self.client_name:
                if self.data.startswith("Name:"):
                    self.client_name = self.data.split(":")[1]
                    with self.lock:
                        self.clients[self.client_name] = self.request
                    self.broadcast(f"{self.client_name} has joined the chat.")
                    self.send_online_users()
                else:
                    self.request.sendall(bytes("Please send your name in the format 'Name: your_name'.\n", "utf-8"))
            else:
                if self.data == "quit":
                    self.request.close()
                    with self.lock:
                        del ChatHandler.clients[self.client_name]
                    self.broadcast(f"{self.client_name} has left the chat.")
                    self.send_online_users()
                    break
                elif self.data.startswith("Chat with:"):
                    self.current_chat_partner = self.data.split(":")[1]
                    self.request.sendall(bytes(f"You are now chatting with {self.current_chat_partner}\n", "utf-8"))
                    self.check_message_buffer()
                elif self.data == "End chat":
                    self.current_chat_partner = None
                    self.request.sendall(bytes("You have ended the current chat\n", "utf-8"))
                elif self.current_chat_partner:
                    recipient_name = self.current_chat_partner
                    message = self.data
                    self.send_private_message(recipient_name.strip(), message.strip())
                else:
                    self.request.sendall(bytes("You are not currently in a chat. Use 'Chat with: username' to start a chat.\n", "utf-8"))

    def broadcast(self, message):
        with self.lock:
            for client_name, client_socket in self.clients.items():
                client_socket.sendall(bytes(message + "\n", "utf-8"))

    def send_online_users(self):
        online_users = ", ".join(self.clients.keys())
        with self.lock:
            for client_name, client_socket in self.clients.items():
                client_socket.sendall(bytes(f"Online users: {online_users}\n", "utf-8"))

    def send_private_message(self, recipient_name, message):
        if recipient_name in self.clients:
            recipient_socket = self.clients[recipient_name]
            recipient_socket.sendall(bytes(f"[Private from {self.client_name}]: {message}\n", "utf-8"))
        else:
            self.request.sendall(bytes(f"User {recipient_name} is not online.\n", "utf-8"))

    def check_message_buffer(self):
        if self.current_chat_partner in self.message_buffer:
            for message in self.message_buffer[self.current_chat_partner]:
                self.request.sendall(bytes(message + "\n", "utf-8"))
            del self.message_buffer[self.current_chat_partner]

HOST, PORT = "localhost", 9989
server = socketserver.ThreadingTCPServer((HOST, PORT), ChatHandler)
try:
    server.serve_forever()
finally:
    server.server_close()
