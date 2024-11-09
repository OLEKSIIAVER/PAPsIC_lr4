import socket
import ssl
import os
import threading

# Шлях до сертифікатів
server_cert = 'server.crt'  # Шлях до сертифіката сервера
server_key = 'server.key'   # Шлях до приватного ключа сервера
ca_cert = 'ca.crt'          # Шлях до сертифіката центру сертифікації (CA)

# Створення SSL-сокета для сервера
def create_ssl_server_socket():
    # Створення SSL-контексту для клієнтської аутентифікації
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH, cafile=ca_cert)
    context.load_cert_chain(certfile=server_cert, keyfile=server_key)  # Завантажуємо сертифікат і ключ сервера
    context.verify_mode = ssl.CERT_NONE  # Вимикаємо перевірку сертифікатів (для тестування, не безпечно на продакшн)

    # Створення звичайного сокета для TCP-з'єднань
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))  # Прив'язка до порту 12345 на localhost
    server_socket.listen(5)  # Сервер слухає до 5 підключень одночасно
    return context.wrap_socket(server_socket, server_side=True)  # Загортаємо сокет у SSL

# Обробка клієнтського підключення
def handle_client(client_socket):
    try:
        while True:
            filename = client_socket.recv(1024).decode('utf-8')  # Отримуємо ім'я файлу від клієнта
            if not filename:  # Якщо файл не надіслано, завершуємо обробку
                break
            print(f"Receiving file: {filename}")
            filepath = os.path.join('cl2_in', filename)  # Шлях для збереження файлу на сервері

            # Відкриваємо файл для запису
            with open(filepath, 'wb') as f:
                while True:
                    chunk = client_socket.recv(1024)  # Читаємо порцію даних з сокета
                    if not chunk:  # Якщо немає даних, файл передано повністю
                        break
                    f.write(chunk)  # Записуємо порцію даних у файл
            print(f"Received file: {filename}")  # Повідомлення про завершення передачі файлу
    except Exception as e:
        print(f"Error with client: {e}")  # Логування помилки, якщо сталася проблема під час передачі
    finally:
        client_socket.close()  # Закриваємо сокет клієнта після завершення обробки

# Основна функція для запуску сервера
def start_server():
    server_socket = create_ssl_server_socket()  # Створюємо SSL-сокет
    print("Server started and listening on port 12345...")

    while True:
        # Приймаємо нове з'єднання
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")  # Логуємо адресу клієнта

        # Створюємо новий потік для обробки клієнта, кожен клієнт обробляється в окремому потоці
        threading.Thread(target=handle_client, args=(client_socket,)).start()

# Запуск сервера
if __name__ == "__main__":
    start_server()
