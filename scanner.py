import subprocess
import sys
import socket
import psutil

def detect_interface_ip():
    """detect local ip and exclude 127.0.0.1."""
    interfaces = psutil.net_if_addrs()
    active_interfaces = psutil.net_if_stats()

    for iface, addresses in interfaces.items():
        # Check for active interface
        if active_interfaces.get(iface, None) and active_interfaces[iface].isup:
            for addr in addresses:
                # Check IPv4 interfaces and exclude localhost (127.0.0.1)
                if addr.family == socket.AF_INET and addr.address != '127.0.0.1':
                    return addr.address

    raise Exception("Network interface not detected")

# Detect network interface
try:
    cible = detect_interface_ip()
except Exception as e:
    continue
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
    ping ip on the network
    """
    ip_parts = cible.split(".")
    ip_parts[3] = 1
    results = []
    while int(ip_parts[3]) < 5: #limit to the first 5 ip
        new_ip = incremental_ip(ip_parts)
        stdout, stderr = ping(new_ip)
        if stderr:
            results.append(f"Error ping to {new_ip}: {stderr}")
        else:
            results.append(f"Response ping to {new_ip}: {stdout}")
    return results

def s_arg(ports):
    """
    scan ports on the network
    """
    ip_parts = cible.split(".")  
    ip_parts[3] = 1  
    results = []
    while int(ip_parts[3]) < 5: #limit to the first 5 ip
        new_ip = incremental_ip(ip_parts)
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
        case "-s":
            ports = [21, 22, 80] 
            resultat = s_arg(ports)