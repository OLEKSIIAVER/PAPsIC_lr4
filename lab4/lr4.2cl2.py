import socket
import ssl
import os
import time

# Шлях до сертифікатів
client_cert = 'client.crt'
client_key = 'client.key'
ca_cert = 'ca.crt'


def create_ssl_client_socket():
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=ca_cert)
    context.load_cert_chain(certfile=client_cert, keyfile=client_key)
    context.check_hostname = False  # Вимикаємо перевірку хоста
    context.verify_mode = ssl.CERT_NONE  # Вимикаємо перевірку сертифікатів для тестів

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssl_socket = context.wrap_socket(client_socket, server_hostname="localhost")
    return ssl_socket

def send_files_from_directory(directory, client_socket):
    # Отримуємо список файлів з директорії
    files = os.listdir(directory)
    for filename in files:
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            print(f"Sending file: {filename}")
            client_socket.send(filename.encode('utf-8'))  # Надсилаємо ім'я файлу
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(1024)  # Читаємо файл порціями
                    if not chunk:
                        break  # Коли файл закінчується
                    client_socket.send(chunk)  # Відправляємо дані
            time.sleep(5)  # Затримка між файлами (5 секунд)
        else:
            print(f"Skipping non-file: {filename}")

def start_client():
    client_socket = create_ssl_client_socket()
    try:
        client_socket.connect(('localhost', 12345))  # Підключення до сервера
        send_files_from_directory('cl2', client_socket)  # Надсилаємо файли з папки 'cl1'
    finally:
        client_socket.close()

if __name__ == "__main__":
    start_client()