
import socket
import sys
import select
import argparse


PORT=22223


READ_BUFFER = 4096
def parse_arguments():
    parser = argparse.ArgumentParser(description='Chat client')
    parser.add_argument('-ip', '--ip', default='localhost', help='Hostname of the server')
    parser.add_argument('-p', '--port', type=int, default=PORT, help='Port of the server')
    parser.add_argument('-n', '--name', help='Your username')
    return parser.parse_args()

def prompt():
    print('>', end=' ', flush=True)

def connect_to_server(ip, port):
    try:
        # Intenta conectar con IPv6
        server_connection = socket.create_connection((ip, port), timeout=5)
        return server_connection
    except Exception as e:
        print(f"Error al conectar con {ip}:{port} utilizando IPv6: {e}")
        try:
            # Si la conexión con IPv6 falla, intenta con IPv4
            ip_v4 = socket.getaddrinfo(ip, port, family=socket.AF_INET)[0][4][0]
            server_connection = socket.create_connection((ip_v4, port), timeout=5)
            return server_connection
        except Exception as e:
            print(f"Error al conectar con {ip} utilizando IPv4: {e}")
            return None

    

if __name__ == "__main__":
    args = parse_arguments()
    server_connection = connect_to_server(args.ip, args.port)
    if server_connection is None:
        print("No se pudo establecer una conexión con el servidor.")
        sys.exit(1)
    # server_connection = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    # server_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # server_connection.connect((args.ip, args.port))
    print("Conectado al servidor\n")

    if args.name:
        name = args.name
        server_connection.sendall(("name: " + name).encode())      

    
    msg_prefix = ''

    socket_list = [sys.stdin, server_connection]



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
