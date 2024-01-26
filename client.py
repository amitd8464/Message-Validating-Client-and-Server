import socket
from sys import * 
import hashlib
import sys

            
def main():
    server_name, server_port, message_filename, signature_filename = argv[1:5]
    
    # READ MESSAGES INTO LIST
    message_list = []
    with open(message_filename, "r") as file:
        while True:
            length_line = file.readline()

            if not length_line:
                break
            msg = file.read(int(length_line))
            msg = msg.replace("\\","\\\\").replace(".", "\\.")
            if msg[-1] == "\n":
                msg = msg[:-1]
            msg += "\r\n"
            message_list.append(msg)

    #READ SIGNATURES INTO LIST
    sig_list = []
    with open(signature_filename, "r") as file: 
        for line in file.readlines():
            line = line.strip()
            sig_list.append(line)

    #CREATE PORT
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_name, int(server_port)))
    
    # SEND HELLO
    sock.send(b"HELLO")
    response = sock.recv(1024)

    #ENSURE SERVER GOT HELLO
    if response.decode() != "260 OK":
        print("Invalid response")
        sock.close()
        sys.exit(1)

    #SEND MESSAGES
    message_counter = 0
    for message in message_list:
        print("DATA")
        sock.send(b"DATA")
        # sock.send(message.encode("utf-8"))
        bytes(message, encoding="utf-8")
        sock.send(message)
        response = sock.recv(1024)

        if response.decode() != "270 SIG":
            print(f"did not recieve 270 sig after DATA cmd")
            sock.close()
            sys.exit(1)
        #print("recieved 270 sig for DATA cmd")

        server_hash = sock.recv(1024).decode()
        #print("checking hash", server_hash, sig_list[message_counter])
        if server_hash == sig_list[message_counter]:
            #print("PASS")
            sock.send(b"PASS")
        else:
            #print("FAIL")
            sock.send(b"FAIL")
        message_counter += 1
        
        response = sock.recv(1024).decode()
        if response != "260 OK":
            print("did not recieve 260 OK after pass/fail")
            sock.close()
            sys.exit(1)
        #print("got 260 OK, moving on to next message")
    #print("QUIT")
    sock.send(b"QUIT")
    sock.close()



if __name__ == "__main__":
    main()