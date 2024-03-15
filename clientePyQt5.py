import sys
import socket
import threading
from PyQt5 import QtWidgets, QtGui, QtCore

class ChatClient(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.client_socket = None
        self.username = None
        self.online_users = []

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Chat")
        self.setGeometry(200, 200, 400, 300)

        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QtWidgets.QVBoxLayout()

        self.username_label = QtWidgets.QLabel("Ingresa tu nombre de usuario:")
        self.layout.addWidget(self.username_label)

        self.username_entry = QtWidgets.QLineEdit()
        self.layout.addWidget(self.username_entry)

        self.connect_button = QtWidgets.QPushButton("Conectar")
        self.connect_button.clicked.connect(self.connect_to_server)
        self.layout.addWidget(self.connect_button)

        self.message_label = QtWidgets.QLabel("Mensaje:")
        self.layout.addWidget(self.message_label)

        self.message_entry = QtWidgets.QLineEdit()
        self.layout.addWidget(self.message_entry)

        self.user_label = QtWidgets.QLabel("Seleccionar usuario:")
        self.layout.addWidget(self.user_label)

        self.user_dropdown = QtWidgets.QComboBox()
        self.layout.addWidget(self.user_dropdown)

        self.send_button = QtWidgets.QPushButton("Enviar")
        self.send_button.clicked.connect(self.send_message)
        self.layout.addWidget(self.send_button)

        self.message_history = QtWidgets.QTextEdit()
        self.message_history.setReadOnly(True)
        self.layout.addWidget(self.message_history)

        self.central_widget.setLayout(self.layout)

    def connect_to_server(self):
        username = self.username_entry.text().strip()
        if not username:
            QtWidgets.QMessageBox.warning(self, "Error", "Por favor, ingresa un nombre de usuario.")
            return

        try:
            host, port = 'localhost', 9999
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host, port))
            self.client_socket.sendall(username.encode('utf-8'))
            self.username = username

            # Mostrar el nombre de usuario
            self.username_label.setText(f"Usuario: {self.username}")

            # Ocultar widgets de conexión
            self.username_label.hide()
            self.username_entry.hide()
            self.connect_button.hide()

            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.start()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Error al conectar al servidor: {e}")

    def send_message(self):
        if not self.client_socket:
            QtWidgets.QMessageBox.warning(self, "Error", "No estás conectado al servidor.")
            return

        selected_user = self.user_dropdown.currentText()
        message = self.message_entry.text().strip()
        if not message:
            QtWidgets.QMessageBox.warning(self, "Error", "Por favor, ingresa un mensaje.")
            return

        full_message = f"{selected_user}:{message}"
        self.client_socket.sendall(full_message.encode('utf-8'))
        self.message_entry.clear()

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message.startswith("USUARIOS:"):
                    self.update_user_list(message[len("USUARIOS:"):])
                else:
                    self.append_to_history(message)
            except Exception as e:
                print(f"Error al recibir mensajes: {e}")
                break

    def update_user_list(self, users):
        self.online_users = users.split(',')
        self.user_dropdown.clear()
        self.user_dropdown.addItems(self.online_users)

    def append_to_history(self, message):
        self.message_history.append(message)


def main():
    app = QtWidgets.QApplication(sys.argv)
    chat_client = ChatClient()
    chat_client.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
