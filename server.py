import socketserver
import threading

class ChatHandler(socketserver.BaseRequestHandler):
    clients = {}
    lock = threading.Lock()

    def handle(self):
        self.client_name = None

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
                elif ":" in self.data:
                    recipient_name, message = self.data.split(":", 1)
                    self.send_private_message(recipient_name.strip(), message.strip())
                else:
                    self.broadcast(f"{self.client_name}: {self.data}")

    def broadcast(self, message):
        with self.lock:
            for client_name, client_socket in self.clients.items():
                if client_socket != self.request:
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


HOST, PORT = "localhost", 9999
server = socketserver.ThreadingTCPServer((HOST, PORT), ChatHandler)
try:
    server.serve_forever()
finally:
    server.server_close()
