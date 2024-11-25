import re
import subprocess
import sys
import socket

def ping(host):
    command = ["ping", host]
    result = subprocess.run(command)
    return result



def scan_port(host, ports):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        test = s.connect_ex((host,ports))
        if test == 0:
            print(f"Port {ports} is open")
        else :
            print(f"port {ports} is closed")

def incremental_ip(list) :
    integer = int(list[3])
    integer += 1
    test[3] = str(integer)
    new = ".".join(test)
    return new

def p_arg() :
    while int(test[3]) <  3 :
                new = incremental_ip(test)
                cible = new
                print(cible)
                resultat = []
                resultat.append(ping(cible))
    return resultat

def s_arg(list) :
    ports = list
    while int(test[3]) < 255 :
        new = incremental_ip(test)
        cible = new
        for i in range(len(ports)) :
            print(cible)
            print(f"ping vers {cible} : {ports[i]}")
            print(cible, ports[i])
            resultat = scan_port(cible, int(ports[i]))
    return resultat


if __name__ == "__main__":
    cible = "172.20.10.0"
    test = cible.split(".")
    match sys.argv[1] :
        case "-p" :
            resultat = p_arg()
            print(resultat)
        case "-s" :
            ports = [21,22,80]
            resultat = s_arg(ports)
        case "-po" :
            resultat = p_arg()
            f = open("results.txt", "w")
            f.write(str(resultat))
            f.close()
        case "-h" :
            print("help")