# Requisitos previos

    Python 3.x instalado en su sistema.

# Instalación

    Clona el repositorio de GitHub:

    bash

git clone https://github.com/AugustoKark/FinalCompuIIAK.git

Navega al directorio de la aplicación:

bash

    cd FinalCompuIIAK

Ejecución del servidor

    Abre una terminal y navega al directorio de la aplicación.

    Ejecuta el siguiente comando para iniciar el servidor:

    bash

    python server.py

    El servidor ahora está en funcionamiento y escuchando en el puerto predeterminado 22223.

Ejecución del cliente

    Abre otra terminal y navega al directorio de la aplicación.

    Ejecuta el siguiente comando para iniciar el cliente:

    bash

python client.py -ip <ip_servidor> -p <puerto_servidor>

    Reemplaza <ip_servidor> y <puerto_servidor> con la dirección IP y el puerto del servidor, respectivamente.

    Por ejemplo, si el servidor está en ejecución en la misma máquina, puedes usar localhost como dirección IP y 22223 como puerto.

    bash

python client.py -ip localhost -p 22223
    
        El cliente ahora está en funcionamiento y conectado al servidor.



Se te pedirá que ingreses un nombre de usuario. Ingresa un nombre y presiona Enter.

o tambien puedes usar el siguiente comando para conectarte al servidor:

    bash

python client.py -ip localhost -p 22223 -n <nombre_usuario>

    Reemplaza <nombre_usuario> con el nombre de usuario que deseas usar.

    Por ejemplo, si deseas conectarte con el nombre de usuario "Alice", puedes usar el siguiente comando:

    bash

python client.py -ip localhost -p 22223 -n Alice

    El cliente ahora está en funcionamiento y conectado al servidor con el nombre de usuario "Alice".

# Uso
Una vez que te hayas unido al servidor, puedes usar los siguientes comandos:

    <list>: Lista todas las salas de chat disponibles.
    <join> nombre_sala: Únete a una sala de chat existente o crea una nueva sala con el nombre especificado.
    <private> nombre_destinatario mensaje: Envía un mensaje privado a otro usuario.
    <history>: Muestra el historial de mensajes de la sala de chat actual.

Para salir de la aplicación, simplemente escribe <quit> y presiona Enter.