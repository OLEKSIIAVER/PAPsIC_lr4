import socket
import ssl
import os
import time

# Шлях до сертифікатів
client_cert = 'client.crt'  # Шлях до сертифіката клієнта
client_key = 'client.key'   # Шлях до приватного ключа клієнта
ca_cert = 'ca.crt'          # Шлях до сертифіката центру сертифікації (CA)

# Функція для створення SSL-сокета для клієнта
def create_ssl_client_socket():
    # Створення SSL-контексту для серверної аутентифікації
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=ca_cert)
    context.load_cert_chain(certfile=client_cert, keyfile=client_key)  # Завантажуємо сертифікат і ключ клієнта
    context.check_hostname = False  # Вимикаємо перевірку хоста (не безпечно для продакшн середовища)
    context.verify_mode = ssl.CERT_NONE  # Вимикаємо перевірку сертифікатів (для тестування)

    # Створення звичайного TCP-сокета
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Обгортаємо сокет в SSL для захищеного з'єднання
    ssl_socket = context.wrap_socket(client_socket, server_hostname="localhost")
    return ssl_socket

# Функція для надсилання файлів з директорії на сервер
def send_files_from_directory(directory, client_socket):
    # Отримуємо список всіх файлів у вказаній директорії
    files = os.listdir(directory)
    for filename in files:
        filepath = os.path.join(directory, filename)  # Отримуємо повний шлях до файлу
        if os.path.isfile(filepath):  # Перевіряємо, чи це файл (не директорія)
            print(f"Sending file: {filename}")
            client_socket.send(filename.encode('utf-8'))  # Надсилаємо ім'я файлу серверу
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(1024)  # Читаємо файл порціями по 1024 байти
                    if not chunk:
                        break  # Якщо файл завершено, зупиняємо передачу
                    client_socket.send(chunk)  # Відправляємо порцію даних на сервер
            time.sleep(5)  # Затримка в 5 секунд між відправленням файлів
        else:
            print(f"Skipping non-file: {filename}")  # Пропускаємо елементи, які не є файлами

# Основна функція для запуску клієнта
def start_client():
    client_socket = create_ssl_client_socket()  # Створюємо SSL-сокет для клієнта
    try:
        # Підключення до сервера на локальному хості, порт 12345
        client_socket.connect(('localhost', 12345))
        # Надсилаємо файли з директорії 'cl1' на сервер
        send_files_from_directory('cl1', client_socket)
    finally:
        client_socket.close()  # Закриваємо сокет після завершення роботи

# Запуск клієнта
if __name__ == "__main__":
    start_client()
