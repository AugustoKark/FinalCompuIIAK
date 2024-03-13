import tkinter as tk
from tkinter import messagebox
import socket
import threading

class ChatGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chat")
        
        self.client_socket = None
        self.username = None
        self.online_users = []  # Inicializamos como una lista vacía
        
        self.create_widgets()

        self.message_history = tk.Text(self.root, state='disabled')
        self.message_history.pack(expand=True, fill=tk.BOTH)
        
    def create_widgets(self):
        self.username_label = tk.Label(self.root, text="Ingresa tu nombre de usuario:")
        self.username_label.pack()
        
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()
        
        self.connect_button = tk.Button(self.root, text="Conectar", command=self.connect_to_server)
        self.connect_button.pack()
        
        # Creamos un OptionMenu vacío por ahora
        self.user_dropdown = tk.OptionMenu(self.root, tk.StringVar(), ())
        self.user_dropdown.pack()
        
        self.message_label = tk.Label(self.root, text="Mensaje:")
        self.message_label.pack()
        
        self.message_entry = tk.Entry(self.root)
        self.message_entry.pack()
        
        self.send_button = tk.Button(self.root, text="Enviar", command=self.send_message)
        self.send_button.pack()
        
    def connect_to_server(self):
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showwarning("Error", "Por favor, ingresa un nombre de usuario.")
            return
        
        # Conectar al servidor
        host, port = 'localhost', 9999
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))

        # Enviar nombre de usuario al servidor
        self.client_socket.sendall(username.encode('utf-8'))
        self.username = username
        
        # Ocultar los widgets de conexión y mostrar la interfaz de chat
        self.username_label.pack_forget()
        self.username_entry.pack_forget()
        self.connect_button.pack_forget()
        
        self.create_chat_widgets()
        
        # Iniciar el hilo para recibir mensajes del servidor
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()
        
    def create_chat_widgets(self):
        # Creamos el OptionMenu con la lista de usuarios en línea
        self.user_var = tk.StringVar(self.root)
        # self.user_dropdown = tk.OptionMenu(self.root, self.user_var, *self.online_users)
        self.user_dropdown = tk.OptionMenu(self.root, self.user_var, ())
        self.user_dropdown.pack()
        
    def update_user_list(self, users):
        self.online_users = users.split(',')
        
        # Actualizamos las opciones del OptionMenu con la lista de usuarios en línea
        self.user_dropdown['menu'].delete(0, tk.END)
        for user in self.online_users:
            self.user_dropdown['menu'].add_command(label=user, command=tk._setit(self.user_var, user))
        
    def send_message(self):
        if not self.client_socket:
            messagebox.showwarning("Error", "No estás conectado al servidor.")
            return
        
        selected_user = self.user_var.get()
        if not selected_user:
            messagebox.showwarning("Error", "Por favor, selecciona un usuario destinatario.")
            return
        
        message = self.message_entry.get().strip()
        if not message:
            messagebox.showwarning("Error", "Por favor, ingresa un mensaje.")
            return
        
        full_message = f"{selected_user}:{message}"
        self.client_socket.sendall(full_message.encode('utf-8'))
        self.message_entry.delete(0, tk.END)
        
    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message.startswith("USUARIOS:"):
                    # Actualizar la lista de usuarios en línea
                    self.update_user_list(message[len("USUARIOS:"):])
                else:
                    # Procesar el mensaje recibido
                    self.append_to_history(message)
                    # pass
            except Exception as e:
                print(f"Error al recibir mensajes: {e}")
                break

    def append_to_history(self, message):
        self.message_history.config(state='normal')
        self.message_history.insert(tk.END, message + '\n')
        self.message_history.config(state='disabled')

    def run(self):
        self.root.mainloop()

# Ejecutar la aplicación
if __name__ == "__main__":
    gui = ChatGUI()
    gui.run()
