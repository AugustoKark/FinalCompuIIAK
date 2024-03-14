import socketserver
import threading

class ChatServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

class ChatHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print(f"Conexión establecida desde {self.client_address}")
        self.request.sendall("Bienvenido al servidor de chat. Ingresa tu nombre: ".encode('utf-8'))
        username = self.request.recv(1024).decode('utf-8').strip()

        # Almacenar la conexión del cliente junto con su nombre de usuario
        clients[username] = self.request

        
        self.broadcast_users()

        while True:
            try:
                message = self.request.recv(1024).decode('utf-8')
                if not message:
                    break

                # Parsear el mensaje para obtener el destinatario
                recipient, message = message.split(':', 1)

                # Verificar si el destinatario está en la lista de clientes
                if recipient in clients:
                    # Reenviar el mensaje al destinatario

                    clients[recipient].sendall(f"{username}: {message}".encode('utf-8'))
                    if recipient != username:
                        self.request.sendall(f"Tú: {message}".encode('utf-8'))
                else:
                    self.request.sendall("El usuario no está conectado.".encode('utf-8'))
            except Exception as e:
                print(f"Error: {e}")
                break

        # Eliminar al cliente desconectado de la lista
        del clients[username]
        self.broadcast_users()

    def broadcast_users(self):
        # Obtener la lista de usuarios en línea
        online_users = ",".join(clients.keys())

        # Enviar la lista de usuarios en línea a todos los clientes
        for client_socket in clients.values():
            client_socket.sendall(f"USUARIOS:{online_users}".encode('utf-8'))

# Configuración del servidor
host, port = 'localhost', 9999
server = ChatServer((host, port), ChatHandler)

# Iniciar el servidor en un hilo separado
server_thread = threading.Thread(target=server.serve_forever)
server_thread.daemon = True
server_thread.start()

print(f"Servidor de chat en ejecución en {host}:{port}")

# Lista de clientes conectados (dentro de la clase ChatHandler)
clients = {}

try:
    while True:
        continue
except KeyboardInterrupt:
    print("Servidor detenido manualmente.")