import sqlite3


# Conectarse a la base de datos (o crearla si no existe)
conn = sqlite3.connect('chat.db')

# Crear una tabla para los usuarios
conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL
    )
''')

# Crear una tabla para las salas de chat
conn.execute('''
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
''')

# Crear una tabla para las relaciones entre usuarios y salas
conn.execute('''
    CREATE TABLE IF NOT EXISTS user_rooms (
        user_id INTEGER NOT NULL,
        room_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (room_id) REFERENCES rooms(id),
        PRIMARY KEY (user_id, room_id)
    )
''')

# Guardar los cambios y cerrar la conexión
conn.commit()
conn.close()
