
import socketserver
import select

from util import Hall, Player, PORT

class ChatHandler(socketserver.StreamRequestHandler):
    def handle(self):
        player = Player(self.request)
        hall.welcome_new(player)
        while True:
            read_sockets, _, _ = select.select([player.socket], [], [])
            for sock in read_sockets:
                msg = sock.recv(4096)
                if not msg:
                    player.socket.close()
                    return
                msg = msg.decode().lower()
                hall.handle_msg(player, msg)


hall = Hall()
server = socketserver.ThreadingTCPServer(('localhost', PORT), ChatHandler)
print("Server listening on port", PORT)
server.serve_forever()
