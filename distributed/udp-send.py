import socket
import sys

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

    sock.sendto(sys.argv[1].encode('UTF-8'), (interface, server_port))
    print('Sent "{}" from port {}'.format(sys.argv[1], port))

