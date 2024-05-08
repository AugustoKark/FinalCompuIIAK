import socketserver
import select
import socket
import os
import threading
from Hall import Hall
from Room import Room
from User import User


MAX_CLIENTS = 30
PORT_IPV4 = 22221
PORT_IPV6 = 22228
QUIT_STRING = '<$quit$>'







class ChatHandler(socketserver.StreamRequestHandler):
    def handle(self):
        user = User(self.request)
        print(f'Conexión establecida desde {self.client_address[0]} en el hilo {threading.current_thread().ident}')
        hall.welcome_new(user)
        
        while True:
            read_sockets, _, _ = select.select([user.socket], [], [])
            for sock in read_sockets:
                msg = sock.recv(4096)
                if not msg:
                    user.socket.close()
                    return
                msg = msg.decode().lower()
                print(threading.current_thread().ident)
                hall.handle_msg(user, msg)


hall = Hall()



class MyIPv4Server(socketserver.ThreadingTCPServer):
    address_family = socket.AF_INET  # Configura el servidor para IPv4

    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        super().server_bind()



class MyIPv6Server(socketserver.ThreadingTCPServer):
    address_family = socket.AF_INET6  # Configura el servidor para IPv6

    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        super().server_bind()

def start_server(host, port, family, ServerClass):
    server = ServerClass((host, port), ChatHandler)
    print(f"Server started on [{host}]:{port}")
    print(threading.current_thread().ident)
    threading.Thread(target=server.serve_forever).start()


# Obtén todas las direcciones IPv4 e IPv6 disponibles
addr_info = socket.getaddrinfo(None, PORT_IPV6, socket.AF_UNSPEC,
                               socket.SOCK_STREAM, socket.IPPROTO_TCP)
print(addr_info)

for family, _, _, _, sockaddr in addr_info:
    host, port = sockaddr[:2]
    ServerClass = MyIPv4Server if family == socket.AF_INET else MyIPv6Server
    try:
        start_server(host, port, family, ServerClass)
     
    except socket.error as e:
        print(f"Error al iniciar el servidor en [{host}]:{port} - {e}")


