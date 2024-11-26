import subprocess
import sys
import socket
import psutil

def detect_interface_ip():
    """Détecte l'IP locale de l'interface réseau active, excluant 127.0.0.1."""
    interfaces = psutil.net_if_addrs()
    active_interfaces = psutil.net_if_stats()

    for iface, addresses in interfaces.items():
        # Vérifie si l'interface est active
        if active_interfaces.get(iface, None) and active_interfaces[iface].isup:
            for addr in addresses:
                # Vérifie les interfaces IPv4 et exclut localhost (127.0.0.1)
                if addr.family == socket.AF_INET and addr.address != '127.0.0.1':
                    return addr.address

    raise Exception("Aucune interface réseau valide détectée.")

# Ajoutez la détection de l'interface réseau ici
try:
    cible = detect_interface_ip()
    print(f"Interface réseau détectée avec IP : {cible}")
except Exception as e:
    print(f"Erreur : {e}")
    sys.exit(1)

def ping(host, count=4, timeout=2):
    """
    Effectue un ping vers l'adresse IP avec un nombre limité de paquets et un temps d'attente.
    :param host: L'adresse IP cible
    :param count: Nombre de paquets à envoyer (par défaut 4)
    :param timeout: Temps d'attente en secondes pour chaque paquet (par défaut 2 secondes)
    :return: Résumé des résultats du ping (succès ou erreur)
    """
    command = ["ping", "-c", str(count), "-W", str(timeout), host]  # "-W" limite le temps d'attente pour chaque paquet
    result = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Lire les résultats de la commande
    stdout, stderr = result.communicate()
    
    if result.returncode == 0:
        # Extraire le résumé des statistiques à la fin du ping
        lines = stdout.decode().strip().split("\n")
        summary = lines[-2:]  # Dernières lignes contenant les statistiques globales
        return "\n".join(summary), None
    else:
        return None, stderr.decode().strip()


def scan_port(host, port):
    """
    Scanne un port sur l'hôte cible.
    :param host: Adresse de l'hôte
    :param port: Port à scanner
    :return: Résultat de la connexion
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        test = s.connect_ex((host, port))
        if test == 0:
            return f"Port {port} is open"
        else:
            return f"Port {port} is closed"

def incremental_ip(ip_parts):
    """
    Incrémente la dernière partie d'une adresse IP et retourne une nouvelle IP.
    :param ip_parts: La liste des parties de l'IP
    :return: La nouvelle adresse IP
    """
    integer = int(ip_parts[3])
    integer += 1
    ip_parts[3] = str(integer)
    new_ip = ".".join(ip_parts)
    return new_ip

def p_arg():
    """
    Ping des adresses IP incrémentales à partir de l'adresse détectée.
    :return: Résultats des pings
    """
    ip_parts = cible.split(".")  # Découpe l'adresse IP en parties
    ip_parts[3] = 1  # Commence à l'adresse suivante
    results = []
    while int(ip_parts[3]) < 5:  # Incrémente jusqu'à la 5ème adresse
        new_ip = incremental_ip(ip_parts)
        print(f"Ping vers : {new_ip}")
        stdout, stderr = ping(new_ip)
        if stderr:
            results.append(f"Erreur ping vers {new_ip}: {stderr}")
        else:
            results.append(f"Réponse ping vers {new_ip}: {stdout}")
    return results

def s_arg(ports):
    """
    Scan des ports pour une plage d'adresses IP incrémentales.
    :param ports: Liste des ports à scanner
    :return: Résultats du scan des ports
    """
    ip_parts = cible.split(".")  # Découpe l'adresse IP en parties
    ip_parts[3] = 1  # Commence à l'adresse suivante
    results = []
    while int(ip_parts[3]) < 5:  # Limite pour éviter des boucles infinies
        new_ip = incremental_ip(ip_parts)
        print(f"Scan de ports pour : {new_ip}")
        for port in ports:
            result = scan_port(new_ip, port)
            results.append(f"{new_ip}:{port} - {result}")
    return results

if __name__ == "__main__":
    cible = str(detect_interface_ip())
    test = cible.split(".")

    # Traitement des arguments
    match sys.argv[1]:
        case "-p":
            resultat = p_arg()
            print(resultat)
        case "-s":
            ports = [21, 22, 80]  # Liste des ports à scanner
            resultat = s_arg(ports)
            print(resultat)
        case "-h":
            print("Utilisation : \n-p pour ping les IP\n-s pour scanner les ports\n-po pour enregistrer les résultats")
