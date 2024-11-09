import socket
import ssl
import time
import os

# Папка з файлами для відправлення
FILES_DIR = "files_to_send"
os.makedirs(FILES_DIR, exist_ok=True)

# Адреса сервера
SERVER_ADDRESS = 'localhost'
SERVER_PORT = 8443


# Функція для надсилання файлу
def send_file(secure_socket, filepath):
    filename = os.path.basename(filepath)  # Отримуємо ім'я файлу
    filesize = os.path.getsize(filepath)  # Отримуємо розмір файлу в байтах

    # Відправка метаданих файлу
    secure_socket.send(f"{filename}:{filesize}".encode("utf-8"))

    # Відправка самого файлу
    with open(filepath, "rb") as f:
        while (chunk := f.read(1024)):
            secure_socket.send(chunk) # Надсилаємо кожну частину файлу

    # Отримання підтвердження від сервера
    response = secure_socket.recv(1024).decode("utf-8")
    print(f"Відповідь від сервера: {response}")


# Ініціалізація клієнтського сокета
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Створення SSL контексту для захищеного з'єднання
ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
ssl_context.check_hostname = False  # Не перевіряємо ім'я хоста
ssl_context.verify_mode = ssl.CERT_NONE  # Не перевіряємо сертифікат сервера

# Перетворення сокета в захищене SSL з'єднання
secure_socket = ssl_context.wrap_socket(client_socket, server_hostname=SERVER_ADDRESS)
secure_socket.connect((SERVER_ADDRESS, SERVER_PORT))# Підключення до сервера

try:
    while True:
        # Знаходимо файли в папці
        files = os.listdir(FILES_DIR)
        for filename in files:
            filepath = os.path.join(FILES_DIR, filename)
            if os.path.isfile(filepath):
                send_file(secure_socket, filepath) # Відправляємо файл на сервер

        # Затримка 2 секунди
        time.sleep(2)

except KeyboardInterrupt:
    print("Клієнт завершено вручну.")
finally:
    secure_socket.close() # Закриваємо з'єднання з сервером
