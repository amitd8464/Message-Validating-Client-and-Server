import socket
import sys
import hashlib

def unescape(msg):
    return msg.replace('\\', '').strip()

def main():

    listen_port, key_file = sys.argv[1:3]
    keys = []
    with open(key_file, "r") as file:
        for line in file.readlines():
            keys.append(line.strip())

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", int(listen_port)))
    sock.listen()
    (conn, address) = sock.accept()
    hello_msg = conn.recv(1024)
    if hello_msg.decode() == "HELLO":
        #print("recieved HELLO")
        #print("260 OK")
        conn.send(b"260 OK")
    else:
        #print(f"{hello_msg} is not a valid HELLO message")
        sock.close()
        sys.exit(1)
    message_counter = 0
    while True:
        client_command = conn.recv(1024).decode()
        match client_command:
            case "DATA":
                #print("recieved data cmd")
                msg = conn.recv(1024).decode()
                msg_lines = msg.rsplit(sep="\n")
                msg_hash = hashlib.sha256()
                for line in msg_lines:
                    if line == ".":
                        #print("end of message")
                        break
                    print(line.encode("ASCII"))
                    msg_hash.update(line.encode("ASCII"))
                #print("hashing with", keys[message_counter].encode("ASCII"))
                msg_hash.update(keys[message_counter].encode("ASCII"))
                #print("computing hash")
                message_counter += 1
                
                #print("270 SIG")
                conn.send(b"270 SIG")
                #print(msg_hash.hexdigest())
                conn.send(msg_hash.hexdigest().encode("ASCII"))
                
                pass_or_fail = conn.recv(1024).decode()
                if pass_or_fail != "PASS" and pass_or_fail != "FAIL":
                    print("invalid: did not recieve pass/fail")
                    sock.close()
                    sys.exit(1)
                #print("260 OK")
                conn.send(b"260 OK")

                
            case "QUIT":
                #print("recieved quit cmd")
                sock.close()
                sys.exit(0)
            case _:
                print(f"recieved invalid cmd: {client_command}")
                sock.close()
                sys.exit(1)



if __name__== "__main__":
    main()