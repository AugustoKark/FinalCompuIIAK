import socket
import sys
import select
import argparse



PORT=22229
READ_BUFFER = 4096


def parse_arguments():
    parser = argparse.ArgumentParser(description='Chat client')
    parser.add_argument('-ip', '--ip', default='192.168.3.160', help='Hostname of the server')
    parser.add_argument('-p', '--port', type=int, default=PORT, help='Port of the server')
    parser.add_argument('-n', '--name', help='Your username')
    return parser.parse_args()

def prompt():
    print('>', end=' ', flush=True)



if __name__ == "__main__":
    args = parse_arguments()
    # '192.168.54.12'
    if '.' in args.ip:
        server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    else:
        server_connection = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

    server_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_connection.connect((args.ip, args.port))
    print("Conectado al servidor\n")

    if args.name:
        name = args.name
        server_connection.sendall(("name: " + name).encode())   
    
    msg_prefix = ''

    socket_list = [sys.stdin, server_connection]


try:
    while True:
        read_sockets, _, _ = select.select(socket_list, [], [])
        for s in read_sockets:
            if s is server_connection: 
                msg = s.recv(READ_BUFFER)
                if not msg:
                    print("Server down!")
                    sys.exit(2)
                else:
                    if msg == b'<$quit$>':
                        sys.stdout.write('Bye\n')
                        sys.exit(2)
                    else:
                        if not (args.name and 'Por favor, ingresa tu nombre:' in msg.decode()):
                            sys.stdout.write(msg.decode())
                        
                        if 'Por favor, ingresa tu nombre:' in msg.decode() and not args.name:
                            msg_prefix = 'name: ' 
                        else:
                            msg_prefix = ''
                        prompt()
            else:
                msg = msg_prefix + sys.stdin.readline()
                server_connection.sendall(msg.encode())
except Exception:
    print("Server down!")
    quit_msg = '<$quit$>'
    server_connection.sendall(quit_msg.encode())
    sys.stdout.write('Bye\n')
    sys.exit(2)