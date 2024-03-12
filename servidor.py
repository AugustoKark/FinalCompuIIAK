import socketserver
import threading

class ChatServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

class ChatHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # Manejar la conexión de un nuevo cliente
        print(f"Conexión establecida desde {self.client_address}")
        self.request.sendall("Bienvenido al servidor de chat. Ingresa tu nombre: ".encode('utf-8'))
        username = self.request.recv(1024).decode('utf-8').strip()

        # Agregar el nuevo cliente a la lista
        clients[username] = self.request

        # Notificar a todos los clientes sobre la nueva conexión
        self.broadcast(f"{username} se ha unido al chat.")

        while True:
            try:
                # Recibir mensajes del cliente
                message = self.request.recv(1024).decode('utf-8')
                if not message:
                    break

                # Reenviar el mensaje a todos los clientes
                self.broadcast(f"{username}: {message}")
            except Exception as e:
                print(f"Error: {e}")
                break

        # Eliminar al cliente desconectado de la lista
        del clients[username]
        self.broadcast(f"{username} se ha desconectado.")

    def broadcast(self, message):
        # Reenviar un mensaje a todos los clientes
        for client in clients.values():
            client.sendall(message.encode('utf-8'))

# Configuración del servidor
host, port = 'localhost', 9999
server = ChatServer((host, port), ChatHandler)

# Lista de clientes conectados
clients = {}

# Iniciar el servidor en un hilo separado
server_thread = threading.Thread(target=server.serve_forever)
server_thread.daemon = True
server_thread.start()

print(f"Servidor de chat en ejecución en {host}:{port}")

# Esperar a que el usuario presione Ctrl+C para detener el servidor
try:
    server_thread.join()
except KeyboardInterrupt:
    print("Servidor detenido.")
    server.shutdown()
    server.server_close()
