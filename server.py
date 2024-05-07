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

START = True
IP_PRUEBA6 = '::'
IP_PRUEBA = '0.0.0.0'





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




class MyServer(socketserver.ThreadingTCPServer):
    def __init__(self, server_address, RequestHandlerClass, ipv6):
        if ipv6:
            self.address_family = socket.AF_INET6
        else:
            self.address_family = socket.AF_INET
        self.ipv6 = ipv6
        super().__init__(server_address, RequestHandlerClass)

    def server_bind(self):
        if self.ipv6:
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        super().server_bind()

def start_server(host, port, ipv6=False):
    server = MyServer((host, port), ChatHandler, ipv6)
    print(f"Server started on [{host}]:{port}")
    server.serve_forever()

# start_server(IP_PRUEBA, PORT_IPV4, False)
start_server(IP_PRUEBA6, PORT_IPV6, True)

# ----------------------------------------------------------------------------

# class MyIPv4Server(socketserver.ThreadingTCPServer):
#     address_family = socket.AF_INET  # Configura el servidor para IPv4

# class MyIPv6Server(socketserver.ThreadingTCPServer):
#     address_family = socket.AF_INET6  # Configura el servidor para IPv6



# def start_ipv4_server():
#     server_ipv4 = MyIPv4Server(('192.168.54.12', PORT_IPV4), ChatHandler)
#     server_ipv4.allow_reuse_address = True
#     print("Servidor IPv4 escuchando en el puerto", PORT_IPV4)
#     print("Identificador del hilo de IPv4:", threading.current_thread().ident)
#     server_ipv4.serve_forever()

# # Crear una función para iniciar el servidor IPv6
# def start_ipv6_server():
#     server_ipv6 = MyIPv6Server(('::', PORT_IPV6), ChatHandler)
#     server_ipv6.allow_reuse_address = True
#     print("Servidor IPv6 escuchando en el puerto", PORT_IPV6)
#     print("Identificador del hilo de IPv6:", threading.current_thread().ident)
#     server_ipv6.serve_forever()
# print(threading.current_thread().ident)

# threading.Thread(target=start_ipv4_server).start()
# threading.Thread(target=start_ipv6_server).start()


# ----------------------------------------------------------------------------