

class User:
    def __init__(self, socket, name="nuevo"):
        socket.setblocking(0)
        self.socket = socket
        self.name = name

    def fileno(self):
        return self.socket.fileno()
