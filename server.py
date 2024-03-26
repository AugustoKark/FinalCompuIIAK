import socketserver
import select
import socket
import os
import threading

MAX_CLIENTS = 30
PORT = 22223
QUIT_STRING = '<$quit$>'


def create_socket(address):
    s = socket.socket(socket.AF_UNSPEC, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setblocking(0)
    s.bind(address)
    s.listen(MAX_CLIENTS)
    print("Servidor escuchando en ", address)
    return s


class Hall:
    def __init__(self):
        self.rooms = {}
        self.room_player_map = {}

    def welcome_new(self, new_player):
        new_player.socket.sendall(b'Bienvenido a la App de Mensajeria.')
        new_player.socket.sendall(b'Por favor, ingresa tu nombre:')

    def list_rooms(self, player):
        if len(self.rooms) == 0:
            msg = 'Lo sentimos pero no hay salas creadas hasta el momento. Crea una!\n' \
                  + 'Usa [<join> room_name] to create a room.\n'
            player.socket.sendall(msg.encode())
        else:
            msg = 'Listando salas actuales...\n'
            for room_name, room in self.rooms.items():
                players_in_room = ", ".join([player.name for player in room.players])
                msg += f'{room_name}: {players_in_room}\n'
            player.socket.sendall(msg.encode())


    def handle_msg(self, player, msg):
        instructions = b'Instrucciones:\n' \
                        + b'[<list>] para listar todas las salas\n' \
                        + b'[<join> room_name] para unirte/crear/cambiar a una sala\n' \
                        + b'[<history>] para ver el historial de chat\n' \
                        + b'[<manual>] para mostrar las instrucciones\n' \
                        + b'[<quit>] para salir\n'

        print(player.name + " dice: " + msg)
        if "name:" in msg:
            name = msg.split()[1]
            player.name = name
            print("Nueva conexion de: ", player.name)
            player.socket.sendall(instructions)

        elif "<join>" in msg:
            same_room = False
            if len(msg.split()) >= 2:
                room_name = msg.split()[1]
                if player.name in self.room_player_map:
                    if self.room_player_map[player.name] == room_name:
                        player.socket.sendall(b'Actualmente estas en la sala: ' + room_name.encode())
                        same_room = True
                    else:
                        old_room = self.room_player_map[player.name]
                        self.rooms[old_room].remove_player(player)
                if not same_room:
                    if not room_name in self.rooms:
                        new_room = Room(room_name)
                        self.rooms[room_name] = new_room
                        # Crear historial de sala si no existe
                        new_room.create_history_file()
                    self.rooms[room_name].players.append(player)
                    self.rooms[room_name].welcome_new(player)
                    self.room_player_map[player.name] = room_name
            else:
                player.socket.sendall(instructions)

        elif "<list>" in msg:
            self.list_rooms(player)

        elif "<manual>" in msg:
            player.socket.sendall(instructions)
        

        elif "<quit>" in msg:
            player.socket.sendall(QUIT_STRING.encode())
            self.remove_player(player)

        elif "<history>" in msg:
            self.show_history(player)

        else:
            if player.name in self.room_player_map:
                current_room = self.room_player_map[player.name]
                self.rooms[current_room].broadcast(player, msg.encode())
                self.rooms[current_room].save_to_history(player.name, msg)  # Save message to history file
            else:
                msg = 'Actualmente no estás en ninguna sala.\n' \
                      + 'Usa [<list>] para ver las salas disponibles.\n' \
                      + 'Usa [<join> room_name] para unirte a una sala.\n'
                player.socket.sendall(msg.encode())

    def remove_player(self, player):
        if player.name in self.room_player_map:
            current_room = self.room_player_map[player.name]
            self.rooms[current_room].remove_player(player)
            del self.room_player_map[player.name]
        print("Jugador: " + player.name + " ha abandonado el chat\n")

    def show_history(self, player):
        if player.name in self.room_player_map:
            current_room = self.room_player_map[player.name]
            self.rooms[current_room].show_history(player)
        else:
            player.socket.sendall('No estás en ninguna sala.\n'.encode())



class Room:
    def __init__(self, name):
        self.players = []
        self.name = name
        self.history_file = os.path.join("chats", name + '_history.txt')

    def welcome_new(self, from_player):
        msg = self.name + " da la bienvenida a: " + from_player.name + '\n'
        for player in self.players:
            player.socket.sendall(msg.encode())

    def broadcast(self, from_player, msg):
        msg = from_player.name.encode() + b":" + msg
        for player in self.players:
            player.socket.sendall(msg)

    def remove_player(self, player):
        self.players.remove(player)
        leave_msg = player.name.encode() + b" ha abandonado la sala\n"
        self.broadcast(player, leave_msg)

    def create_history_file(self):
        if not os.path.exists("chats"):
            os.makedirs("chats")
        with open(self.history_file, 'w'):
            pass

    def save_to_history(self, player_name, message):
        with open(self.history_file, 'a') as file:
            file.write(player_name + ": " + message + "\n")

    def show_history(self, player):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as file:
                history = file.read()
                player.socket.sendall(history.encode())
        else:
            player.socket.sendall(b'No hay historial de chat disponible para esta sala.\n')


class Player:
    def __init__(self, socket, name="nuevo"):
        socket.setblocking(0)
        self.socket = socket
        self.name = name

    def fileno(self):
        return self.socket.fileno()


class ChatHandler(socketserver.StreamRequestHandler):
    def handle(self):
        player = Player(self.request)
        print(f'Conexión establecida desde {self.client_address[0]} en el hilo {threading.current_thread().ident}')
        hall.welcome_new(player)
        
        while True:
            read_sockets, _, _ = select.select([player.socket], [], [])
            for sock in read_sockets:
                msg = sock.recv(4096)
                if not msg:
                    player.socket.close()
                    return
                msg = msg.decode().lower()
                print(threading.current_thread().ident)
                hall.handle_msg(player, msg)


hall = Hall()
server = socketserver.ThreadingTCPServer(('localhost', PORT), ChatHandler)
server.allow_reuse_address = True
print("Servidor escuchando en el puerto", PORT)
server.serve_forever()
