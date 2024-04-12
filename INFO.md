## Informe de Diseño -

Este documento proporciona una visión general de las decisiones principales de diseño tomadas durante el desarrollo de la app de mensajería, así como su justificación.
Modelo de Datos

El modelo de datos de la App se basa en tres entidades principales: Usuario, Sala y Mensaje.

    Usuario: Representa a un usuario de la aplicación, identificado por un nombre único.
    Sala: Representa una sala de chat donde los usuarios pueden comunicarse entre sí.
    Mensaje: Representa un mensaje enviado por un usuario en una sala de chat.

Justificación

Este modelo de datos se consideró adecuado debido a su simplicidad y su capacidad para manejar las características básicas de una aplicación de mensajería. Permite la identificación única de usuarios, la gestión de múltiples salas de chat y el seguimiento de los mensajes enviados.
Almacenamiento de Datos

La App utiliza un enfoque de almacenamiento de datos basado en archivos para mantener el historial de chat de cada sala.

    Cada sala de chat tiene su propio archivo de historial, donde se almacenan los mensajes anteriores.
    Los archivos de historial se guardan en el sistema de archivos del servidor.

Justificación

Se optó por este enfoque de almacenamiento de datos debido a su simplicidad y eficiencia. Los archivos de historial proporcionan una forma sencilla de almacenar y recuperar mensajes anteriores sin la necesidad de configurar una base de datos completa. Además, al mantener los archivos de historial en el sistema de archivos del servidor, se evita la necesidad de utilizar recursos adicionales de almacenamiento externo.
Multithreading

La App utiliza el módulo socketserver de Python para implementar un servidor TCP multi-hilo.

    Cada conexión de cliente se maneja en un hilo separado.
    Esto permite que el servidor maneje múltiples clientes simultáneamente sin bloquear el hilo principal.

Justificación

El uso de un servidor multi-hilo permite una mayor escalabilidad y capacidad de respuesta en la aplicación. Permite que múltiples usuarios se conecten y se comuniquen simultáneamente sin afectar negativamente al rendimiento del servidor. Además, simplifica la lógica de programación al separar la gestión de cada conexión de cliente en hilos independientes.