FROM python:3.11.9-slim
WORKDIR /app
COPY server.py /app
COPY Hall.py /app
COPY Room.py /app
COPY User.py /app

EXPOSE 22228
ENTRYPOINT ["python", "server.py"]

