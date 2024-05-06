import socketserver
import select
import socket
import os
import threading


MAX_CLIENTS = 30
PORT_IPV4 = 22221
PORT_IPV6 = 22228
QUIT_STRING = '<$quit$>'

START = True
IP_PRUEBA6 = '::'
IP_PRUEBA = 'localhost'







class Hall:
    def __init__(self):
        self.rooms = {}
        self.room_user_map = {}
        self.rooms_with_password = {}
       

    def create_room(self, user, room_name, password=None):
        if room_name in self.rooms:
            user.socket.sendall(b'Ya existe una sala con ese nombre.\n')
        else:
            new_room = Room(room_name, password)
            self.rooms[room_name] = new_room
            new_room.create_history_file()
            new_room.users.append(user)
            new_room.welcome_new(user)
            self.room_user_map[user.name] = room_name
            if password:
                self.rooms_with_password[room_name] = password
                print("sala con contraseña creada", room_name)
            msg = 'Sala creada con éxito.\n'
            user.socket.sendall(msg.encode())

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
                if room_name in self.rooms_with_password:
                    room_name = '(privated) ' + room_name
                    users_in_room = ''
                else:
                    room_name = '(public) ' + room_name
                    users_in_room = ", ".join([user.name for user in room.users])
                msg += f'{room_name}: {users_in_room}\n'
            user.socket.sendall(msg.encode())


    def handle_msg(self, user, msg):
        # with self.lock:
            instructions = b'Instrucciones:\n' \
                            + b'[<list>] para listar todas las salas\n' \
                            + b'[<join> room_name] para unirte/crear/cambiar a una sala\n' \
                            + b'[<private> room_name password] para crear una sala con contrasenia\n' \
                            + b'[<history>] para ver el historial de chat\n' \
                            + b'[<private_msg>] para enviar un mensaje privado\n' \
                            + b'[<manual>] para mostrar las instrucciones\n' \
                            + b'[<quit>] para salir\n'

            print(user.name + " dice: " + msg)
            if "name:" in msg:
                name = msg.split()[1]
                user.name = name
                print("Nueva conexion de: ", user.name)
                user.socket.sendall(instructions)

            elif "<join>" in msg:
                try:
                    if len(msg.split()) >= 3:
                        room_name = msg.split()[1]
                        password = msg.split()[2]

                        if room_name in self.rooms_with_password:
                            if password != self.rooms_with_password[room_name]:
                                user.socket.sendall(b'Password incorrecta. Intenta nuevamente.\n')
                                return
                            else:
                                user.socket.sendall(b'Password correcta. Bienvenido a la sala.\n')
                                self.rooms[room_name].users.append(user)
                                self.rooms[room_name].welcome_new(user)
                                self.room_user_map[user.name] = room_name
                                return
                except:
                    print("Error")

                same_room = False
                if len(msg.split()) >= 2:
                    room_name = msg.split()[1]
                    if room_name in self.rooms_with_password:
                        user.socket.sendall(b'Esta sala esta protegida por Password. Por favor, ingresa la Password de la siguiente forma:\n <join> room_name password\n')

                    if user.name in self.room_user_map:
                        if self.room_user_map[user.name] == room_name:
                            user.socket.sendall(b'Actualmente estas en la sala: ' + room_name.encode())
                            same_room = True
                        else:
                            old_room = self.room_user_map[user.name]
                            self.rooms[old_room].remove_user(user)
                    if not same_room and not room_name in self.rooms_with_password:
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

            elif "<private>" in msg:
                if len(msg.split()) >= 3:
                    room_name = msg.split()[1]
                    password = msg.split()[2]
                    if user.name in self.room_user_map:
                        current_room = self.room_user_map[user.name]
                        self.rooms[current_room].remove_user(user)
                    self.create_room(user, room_name, password)

                else:
                    user.socket.sendall(b'Uso incorrecto del comando create. Ejemplo: <create> room_name password\n')
            elif "<private_msg>" in msg:
                if len(msg.split()) >= 3:
                    recipient_name = msg.split()[1]
                    message = ' '.join(msg.split()[2:])
                    if recipient_name in self.room_user_map:
                        recipient_room = self.room_user_map[recipient_name]
                        recipient = [u for u in self.rooms[recipient_room].users if u.name == recipient_name][0]
                        msg = f'Private "{message}" from "{user.name}"'
                        recipient.socket.sendall(msg.encode())
                    else:
                        user.socket.sendall(b'El destinatario no existe.\n')
                else:
                    user.socket.sendall(b'Uso incorrecto del comando private_msg. Ejemplo: <private_msg> destinatario message\n')

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
    def __init__(self, name, password=None):
        self.users = []
        self.name = name
        self.history_file = os.path.join("chats", name + '_history.txt')
        self.password = password
        self.history_lock = threading.Lock()

    def welcome_new(self, from_user):
   
        msg = self.name + " da la bienvenida a: " + from_user.name + '\n'
        
        for user in self.users:
            user.socket.sendall(msg.encode())
        return True

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
        with self.history_lock:
            with open(self.history_file, 'a') as file:
                file.write(user_name + ": " + message )

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