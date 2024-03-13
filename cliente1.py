import socket
import threading

def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            print(message)
        except Exception as e:
            print(f"Error al recibir mensajes: {e}")
            break

def send_messages():
    while True:
        message = input()
        # Seleccionar el destinatario y enviar el mensaje con el formato "destinatario:mensaje" 
        client_socket.sendall(message.encode('utf-8'))

# Conectar al servidor
host, port = 'localhost', 9999
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))

# Ingresar nombre de usuario
username = input("Ingresa tu nombre de usuario: ")
client_socket.sendall(username.encode('utf-8'))

# Iniciar hilos para enviar y recibir mensajes simultáneamente
receive_thread = threading.Thread(target=receive_messages)
send_thread = threading.Thread(target=send_messages)

receive_thread.start()
send_thread.start()

# Esperar a que ambos hilos finalicen
receive_thread.join()
send_thread.join()

# Cerrar la conexión al salir
client_socket.close()
