import socket


with socket.socket(type=socket.SOCK_DGRAM) as sock:
    interface = '127.0.0.1'
    server_port = 9000

    bound = False
    port = server_port + 1
    while not bound:
        try:
            sock.bind((interface, port))
            bound = True
        except OSError:
            port += 1
    print("Listening on port {}".format(port))

    sock.sendto(b"", (interface, server_port))

    while True:
        print(sock.recv(4096))

