import socket

with socket.socket(type=socket.SOCK_DGRAM) as sock:
    address = ('127.0.0.1', 9000)
    sock.bind(address)

    known_addresses = set()
    while True:
        data, sender = sock.recvfrom(4096)
        print('Recieved "{}" from {}'.format(data, sender[1]))
        known_addresses.add(sender)
        if len(data) == 0: continue # Ignore blank messages...
        for addr in known_addresses:
            if addr != sender:
                sock.sendto(data, addr)

