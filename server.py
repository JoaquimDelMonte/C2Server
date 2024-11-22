import socket
import sys

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
        s.listen(5) # 5 is the number of bad connections it will tolerate before refusing new connections

    except socket.error as msg:
        print("Socket Binding error" + str(msg) + "\n" + "Retrying...")
        bind_socket()     


# Establish connection with a client (socket must be listening)
def socket_accept():
    conn, address = s.accept()
    print("Connection has been established! |" + " IP " + address[0] + " | Port " + str(address[1]))
    send_commands(conn)
    conn.close()

def send_commands(conn):
    while True:
        # if the command is quit, close the connection
        cmd = input()
        if cmd == 'quit':
            conn.close()
            s.close()
            sys.exit()

        # if the command is not null and not quit, send the command to the client
        if len(str.encode(cmd)) > 0:
            conn.send(str.encode(cmd))
            client_response = str(conn.recv(1024), "utf-8")
            print(client_response, end="")


def main():
    create_socket()
    bind_socket()
    socket_accept()


main()

