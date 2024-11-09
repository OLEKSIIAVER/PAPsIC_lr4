import socket
import ssl
import threading
import os

# Шлях до сертифіката та ключа для SSL/TLS шифрування
CERT_FILE = "cert1.pem"
KEY_FILE = "key1.pem"

# Папка для збереження отриманих файлів
RECEIVED_FILES_DIR = "received_files"
os.makedirs(RECEIVED_FILES_DIR, exist_ok=True) # Створюємо папку

# Ініціалізація серверного сокета
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 8443))  # Прив'язуємо сервер до порту 8443
server_socket.listen(5)  # Сервер готовий прийняти 5 підключень

# Створення SSL контексту для забезпечення захищеного з'єднання
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE) # Завантажуємо сертифікат та ключ

print("Сервер запущено та чекає на з'єднання...")


# Обробка клієнтських з'єднань
def handle_client(secure_socket, addr):
    print(f"З'єднання з: {addr}")
    try:
        while True:
            # Отримання даних
            file_info = secure_socket.recv(1024).decode("utf-8")
            if not file_info:
                break # Якщо дані не надійшли, закриваємо з'єднання

            # Розділяємо інформацію про файл (ім'я та розмір)
            filename, filesize = file_info.split(":")
            filename = os.path.basename(filename)  # Отримуємо тільки ім'я файлу (без шляху)
            filesize = int(filesize)  # Розмір файлу в байтах
            print(f"Отримання файлу {filename} розміром {filesize} байтів")

            # Прийом файлу та збереження його на сервері
            with open(os.path.join(RECEIVED_FILES_DIR, filename), "wb") as f:
                remaining = filesize
                while remaining > 0:
                    chunk_size = 1024 if remaining >= 1024 else remaining
                    data = secure_socket.recv(chunk_size)
                    if not data:
                        break
                    f.write(data)
                    remaining -= len(data) # Віднімаємо кількість прийнятих байтів

            print(f"Файл {filename} успішно збережено")
            secure_socket.send(f"Файл {filename} отримано".encode("utf-8"))
    except Exception as e:
        print("Помилка:", e)
    finally:
        secure_socket.close() # Закриваємо з'єднання з клієнтом
        print(f"З'єднання з {addr} завершено.")

# Основний цикл сервера, що приймає з'єднання
while True:
    # Прийом клієнтського підключення
    client_socket, addr = server_socket.accept()
    # Перетворення сокета в захищене SSL з'єднання
    secure_socket = ssl_context.wrap_socket(client_socket, server_side=True)
    # Створення окремого потоку для кожного клієнта
    client_thread = threading.Thread(target=handle_client, args=(secure_socket, addr))
    client_thread.start()
