import subprocess
import sys
import socket
import psutil

def detect_interface_ip():
    """detect local ip and exclude 127.0.0.1."""
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
    ping target address with a limit ammount of packets
    """
    command = ["ping", "-c", str(count), "-W", str(timeout), host]  # "-W" limit time for each ping and -c limit number of ping
    result = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # read result
    stdout, stderr = result.communicate()
    
    if result.returncode == 0:
        # extract result
        lines = stdout.decode().strip().split("\n")
        summary = lines[-2:]
        return "\n".join(summary), None
    else:
        return None, stderr.decode().strip()


def scan_port(host, port):
    """
    scan ports on target ip
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        test = s.connect_ex((host, port))
        if test == 0:
            return f"Port {port} is open"
        else:
            return f"Port {port} is closed"

def incremental_ip(ip_parts):
    """
    add 1 to last ip
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
    ip_parts = cible.split(".")
    ip_parts[3] = 1
    results = []
    while int(ip_parts[3]) < 5:  
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
    ip_parts = cible.split(".")  
    ip_parts[3] = 1  
    results = []
    while int(ip_parts[3]) < 5: 
        new_ip = incremental_ip(ip_parts)
        print(f"Scan de ports pour : {new_ip}")
        for port in ports:
            result = scan_port(new_ip, port)
            results.append(f"{new_ip}:{port} - {result}")
    return results

if __name__ == "__main__":
    cible = str(detect_interface_ip())
    test = cible.split(".")


    match sys.argv[1]:
        case "-p":
            resultat = p_arg()
            print(resultat)
        case "-s":
            ports = [21, 22, 80] 
            resultat = s_arg(ports)
            print(resultat)
        case "-h":
            print("Utilisation : \n-p pour ping les IP\n-s pour scanner les ports\n-po pour enregistrer les résultats")
