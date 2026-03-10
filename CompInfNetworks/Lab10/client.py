import socket

HOST = "127.0.0.1"
PORT = 9091

def start_client():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
        print("Підключення встановлено.\n")

        while True:
            data = client.recv(1024)
            if not data:
                break

            text = data.decode()

            print(text, end="")

            if "Сервер завершує роботу" in text:
                break

            if text.endswith(": ") or text.endswith("> "):
                user_input = input()
                client.send(user_input.encode())

    except Exception as e:
        print("Помилка:", e)

    finally:
        client.close()
        print("\nЗ'єднання закрито.")

start_client()
