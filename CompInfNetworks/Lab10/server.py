import socket
import threading
import datetime

HOST = "127.0.0.1"
PORT = 9091

USER_DATA = {
    "vlad": {"pin": "1234", "balance": 5000},
    "anna": {"pin": "9999", "balance": 12000}
}

active_clients = []

def log(msg):
    time = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{time}] {msg}")

def handle_client(conn, addr):
    active_clients.append(conn)
    log(f"[ПІДКЛЮЧЕННЯ] IP={addr[0]} PORT={addr[1]}")

    try:
        while True:
            conn.send("Введіть ім'я користувача: ".encode())
            username = conn.recv(1024).decode().strip()

            if username in USER_DATA:
                conn.send("Користувача знайдено.\n".encode())
                log(f"[OK] Користувач '{username}' підтверджений")
                break
            else:
                conn.send("Користувача не знайдено. Спробуйте ще раз.\n".encode())
                log(f"[WARN] Невідомий користувач '{username}'")

        while True:
            conn.send("Введіть PIN-код: ".encode())
            pin = conn.recv(1024).decode().strip()

            if pin == USER_DATA[username]["pin"]:
                conn.send("Авторизація успішна.\n".encode())
                log(f"[AUTH] Авторизація успішна для '{username}'")
                break
            else:
                conn.send("Невірний PIN. Спробуйте ще раз.\n".encode())
                log(f"[FAIL] Невірний PIN для '{username}'")

        while True:
            menu = (
                "\nОберіть дію:\n"
                "1 - Переглянути баланс\n"
                "2 - Поповнити баланс\n"
                "3 - Зняти кошти\n"
                "4 - Вихід\n> "
            )
            conn.send(menu.encode())
            choice = conn.recv(1024).decode().strip()

            if not choice:
                break

            if choice == "1":
                balance = USER_DATA[username]['balance']
                conn.send(f"Ваш баланс: {balance} грн\n".encode())
                log(f"[INFO] Баланс '{username}': {balance}")

            elif choice == "2":
                conn.send("Введіть суму поповнення:\n> ".encode())
                try:
                    amount = int(conn.recv(1024).decode())
                    USER_DATA[username]['balance'] += amount
                    conn.send("Баланс оновлено.\n".encode())
                    log(f"[DEPOSIT] {username} +{amount}")
                except:
                    conn.send("Некоректне число.\n".encode())

            elif choice == "3":
                conn.send("Скільки зняти?\n> ".encode())
                try:
                    amount = int(conn.recv(1024).decode())
                    if amount <= USER_DATA[username]["balance"]:
                        USER_DATA[username]["balance"] -= amount
                        conn.send("Операція виконана.\n".encode())
                        log(f"[WITHDRAW] {username} -{amount}")
                    else:
                        conn.send("Недостатньо коштів.\n".encode())
                except:
                    conn.send("Некоректне число.\n".encode())

            elif choice == "4":
                conn.send("Вихід із системи.\n".encode())
                break

            else:
                conn.send("Невірна команда. Спробуйте ще раз.\n".encode())

    except:
        pass

    finally:
        if conn in active_clients:
            active_clients.remove(conn)
        conn.close()
        log(f"[СЕСІЮ ЗАВЕРШЕНО] Користувач {addr} відключено.")


def start_server():
    while True:
        print("Оберіть режим сервера:")
        print("S - послідовний")
        print("P - паралельний")

        mode = input("Введіть режим: ").strip().upper()

        if mode in ("S", "P"):
            break
        else:
            print("Невірний режим. Дозволені лише S або P.\n")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)

    log(f"[СТАРТ] Сервер працює на {HOST}:{PORT}")
    log("Для зупинки введіть STOP")

    def stop_listener():
        while True:
            cmd = input()
            if cmd.lower() == "stop":
                log("[ЗУПИНКА] Сервер відправляє повідомлення всім клієнтам...")

                for c in active_clients:
                    try:
                        c.send("\nСервер завершує роботу. З'єднання буде закрито.\n".encode())
                        c.close()
                    except:
                        pass

                active_clients.clear()

                server.close()
                log("[ГОТОВО] Сервер вимкнено.")
                exit(0)

    threading.Thread(target=stop_listener, daemon=True).start()

    while True:
        try:
            conn, addr = server.accept()
        except OSError:
            break

        if mode == "P":
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            log(f"[ПОТОКИ] Активних потоків: {threading.active_count() - 1}")
        else:
            handle_client(conn, addr)

if __name__ == "__main__":
    start_server()