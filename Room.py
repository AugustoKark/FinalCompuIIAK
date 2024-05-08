import os
import threading

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
            if user.socket.fileno() != -1:
                user.socket.sendall(msg)

    def remove_user(self, user):
        if user in self.users:
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

