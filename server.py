import socketserver
import select
import socket
import os
import threading

MAX_CLIENTS = 30
PORT_IPV4 = 22223
PORT_IPV6 = 22224
QUIT_STRING = '<$quit$>'


def create_socket(address):
    s = socket.socket(socket.AF_UNSPEC, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setblocking(0)
    s.bind(address)
    s.listen(MAX_CLIENTS)
    print("Servidor escuchando en ", address)
    return s

class MyIPv4Server(socketserver.ThreadingTCPServer):
    address_family = socket.AF_INET  # Configura el servidor para IPv4

class MyIPv6Server(socketserver.ThreadingTCPServer):
    address_family = socket.AF_INET6  # Configura el servidor para IPv6


class Hall:
    def __init__(self):
        self.rooms = {}
        self.room_user_map = {}

    def welcome_new(self, new_user):
        new_user.socket.sendall(b'Bienvenido a la App de Mensajeria.')
        new_user.socket.sendall(b'Por favor, ingresa tu nombre:')

    def list_rooms(self, user):
        if len(self.rooms) == 0:
            msg = 'Lo sentimos pero no hay salas creadas hasta el momento. Crea una!\n' \
                  + 'Usa [<join> room_name] to create a room.\n'
            user.socket.sendall(msg.encode())
        else:
            msg = 'Listando salas actuales...\n'
            for room_name, room in self.rooms.items():
                users_in_room = ", ".join([user.name for user in room.users])
                msg += f'{room_name}: {users_in_room}\n'
            user.socket.sendall(msg.encode())


    def handle_msg(self, user, msg):
        instructions = b'Instrucciones:\n' \
                        + b'[<list>] para listar todas las salas\n' \
                        + b'[<join> room_name] para unirte/crear/cambiar a una sala\n' \
                        + b'[<history>] para ver el historial de chat\n' \
                        + b'[<manual>] para mostrar las instrucciones\n' \
                        + b'[<quit>] para salir\n'

        print(user.name + " dice: " + msg)
        if "name:" in msg:
            name = msg.split()[1]
            user.name = name
            print("Nueva conexion de: ", user.name)
            user.socket.sendall(instructions)

        elif "<join>" in msg:
            same_room = False
            if len(msg.split()) >= 2:
                room_name = msg.split()[1]
                if user.name in self.room_user_map:
                    if self.room_user_map[user.name] == room_name:
                        user.socket.sendall(b'Actualmente estas en la sala: ' + room_name.encode())
                        same_room = True
                    else:
                        old_room = self.room_user_map[user.name]
                        self.rooms[old_room].remove_user(user)
                if not same_room:
                    if not room_name in self.rooms:
                        new_room = Room(room_name)
                        self.rooms[room_name] = new_room
                        # Crear historial de sala si no existe
                        new_room.create_history_file()
                    self.rooms[room_name].users.append(user)
                    self.rooms[room_name].welcome_new(user)
                    self.room_user_map[user.name] = room_name
            else:
                user.socket.sendall(instructions)

        elif "<list>" in msg:
            self.list_rooms(user)

        elif "<manual>" in msg:
            user.socket.sendall(instructions)
        

        elif "<quit>" in msg:
            user.socket.sendall(QUIT_STRING.encode())
            self.remove_user(user)

        elif "<history>" in msg:
            self.show_history(user)

        else:
            if user.name in self.room_user_map:
                current_room = self.room_user_map[user.name]
                self.rooms[current_room].broadcast(user, msg.encode())
                self.rooms[current_room].save_to_history(user.name, msg)  # Save message to history file
            else:
                msg = 'Actualmente no estás en ninguna sala.\n' \
                      + 'Usa [<list>] para ver las salas disponibles.\n' \
                      + 'Usa [<join> room_name] para unirte a una sala.\n'
                user.socket.sendall(msg.encode())

    def remove_user(self, user):
        if user.name in self.room_user_map:
            current_room = self.room_user_map[user.name]
            self.rooms[current_room].remove_user(user)
            del self.room_user_map[user.name]
        print("Usuario: " + user.name + " ha abandonado el chat\n")

    def show_history(self, user):
        if user.name in self.room_user_map:
            current_room = self.room_user_map[user.name]
            self.rooms[current_room].show_history(user)
        else:
            user.socket.sendall('No estás en ninguna sala.\n'.encode())



class Room:
    def __init__(self, name):
        self.users = []
        self.name = name
        self.history_file = os.path.join("chats", name + '_history.txt')

    def welcome_new(self, from_user):
        msg = self.name + " da la bienvenida a: " + from_user.name + '\n'
        for user in self.users:
            user.socket.sendall(msg.encode())

    def broadcast(self, from_user, msg):
        msg = from_user.name.encode() + b":" + msg
        for user in self.users:
            user.socket.sendall(msg)

    def remove_user(self, user):
        self.users.remove(user)
        leave_msg = user.name.encode() + b" ha abandonado la sala\n"
        self.broadcast(user, leave_msg)

    def create_history_file(self):
        if not os.path.exists("chats"):
            os.makedirs("chats")
        with open(self.history_file, 'w'):
            pass

    def save_to_history(self, user_name, message):
        with open(self.history_file, 'a') as file:
            file.write(user_name + ": " + message + "\n")

    def show_history(self, user):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as file:
                history = file.read()
                user.socket.sendall(history.encode())
        else:
            user.socket.sendall(b'No hay historial de chat disponible para esta sala.\n')


class User:
    def __init__(self, socket, name="nuevo"):
        socket.setblocking(0)
        self.socket = socket
        self.name = name

    def fileno(self):
        return self.socket.fileno()


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
# server = socketserver.ThreadingTCPServer(('localhost', PORT), ChatHandler)
# server.allow_reuse_address = True
# print("Servidor escuchando en el puerto", PORT)
# server.serve_forever()

server_ipv4 = MyIPv4Server(('0.0.0.0', PORT_IPV4), ChatHandler)
server_ipv4.allow_reuse_address = True
print("Servidor IPv4 escuchando en el puerto", PORT_IPV4)
# print("Identificador del hilo de IPv4:", threading.current_thread().ident)

# Crear un servidor IPv6
server_ipv6 = MyIPv6Server(('::', PORT_IPV6), ChatHandler)
server_ipv6.allow_reuse_address = True
print("Servidor IPv6 escuchando en el puerto", PORT_IPV6)
# print("Identificador del hilo de IPv6:", threading.current_thread().ident)
# Iniciar ambos servidores en hilos separados
threading.Thread(target=server_ipv4.serve_forever).start()


threading.Thread(target=server_ipv6.serve_forever).start()



