#!/usr/bin/env python3
import socket

# Configuration du serveur
HOST = '0.0.0.0'
PORT = 9999

def start_server():
    """
    Démarre le serveur et gère les connexions des clients.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"Binding du port: {PORT}")

        conn, addr = s.accept()
        print(f"Connexion établie! | IP: {addr[0]} | Port: {addr[1]}")
        with conn:
            while True:
                try:
                    command = input("Shell> ").strip()
                    if not command:
                        continue
                    conn.send(command.encode() + b"\n")
                    if command == "exit":
                        break
                    data = conn.recv(4096).decode()
                    print(data, end="")
                except KeyboardInterrupt:
                    print("Exiting...")
                    break


if __name__ == "__main__":
    start_server()
