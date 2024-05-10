from Room import Room
from User import User
import os
import threading

QUIT_STRING = '<$quit$>'

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
                            + b'[<private> room_name password] para crear una sala con password\n' \
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
                        msg = f'Private "{message}" from "{user.name}"\n'
                        recipient.socket.sendall(msg.encode())
                        user.socket.sendall(b'\n')
                    else:
                        user.socket.sendall(b'El destinatario no existe.\n')
                else:
                    user.socket.sendall(b'Uso incorrecto del comando private_msg. Ejemplo: <private_msg> destinatario message\n')

            elif "<quit>" in msg:
                user.socket.sendall(QUIT_STRING.encode())
                self.remove_user(user)
                user.socket.close()

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
            print("Usuario: " + user.name + " ha abandonado el chat \n")

    def show_history(self, user):
        if user.name in self.room_user_map:
            current_room = self.room_user_map[user.name]
            self.rooms[current_room].show_history(user)
        else:
            user.socket.sendall('No estás en ninguna sala.\n'.encode())

