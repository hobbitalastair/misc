""" A simple distributed system to demonstrate concurrency.

    Author:     Alastair Hughes
    Contact:    hobbitalastair at yandex dot com
"""

import socket
from threading import Thread, Lock

interface = '127.0.0.1'
server_port = 9000
bufsize = 4096

def connect():
    """ Connect to the main server """
    sock = socket.socket(type=socket.SOCK_DGRAM)

    bound = False
    port = server_port + 1
    while not bound:
        try:
            sock.bind((interface, port))
            bound = True
        except OSError:
            port += 1

    # TODO: This may not be a reliable way of telling the server we exist!
    sock.sendto(b"", (interface, server_port))

    print("Connected on port {}".format(port))
    return sock, port

def publish(sock, value):
    """ Publish our current value.
    
        This also acts as a query provided the other servers are configured to respond
        if they have a more recent version.
    """
    sock.sendto(value.__str__().encode('UTF-8'), (interface, server_port))


def handle_user_input(value, lock, sock):
    """ Handle any user input """
    while True:
        try:
            user_value = int(input())
        except:
            print("Integer required")
            continue
        with lock:
            value.update(user_value, value.version + 1)
            copy = VersionedValue(value.value, value.version)
        publish(sock, copy)


def handle_socket_input(value, lock, sock):
    """ Get input from the socket """
    while True:
        try:
            msg = bytes.decode(sock.recv(bufsize), 'UTF-8')
            sock_value, sock_version = [int(v) for v in msg.split(":")]
        except Exception as e:
            print("Warning: failed to read from socket: {}".format(e))
            continue

        lock.acquire()
        if sock_version > value.version:
            value.update(sock_value, sock_version)
            lock.release()
        if sock_version < value.version:
            copy = VersionedValue(value.value, value.version)
            lock.release()
            publish(sock, copy)


class VersionedValue:
    """ A versioned value """

    def __init__(self, value, version):
        self.value = value
        self.version = version

    def update(self, r_value, r_version):
        self.value = r_value
        self.version = r_version
        print("Updated to {}:{}".format(r_value, r_version))

    def __str__(self):
        return "{}:{}".format(self.value, self.version)


def main():
    sock, port = connect()
    value = VersionedValue(0, 0)
    lock = Lock()

    Thread(target=handle_user_input, args=(value, lock, sock)).start()
    publish(sock, value)
    handle_socket_input(value, lock, sock)

    
if __name__ == "__main__":
    main()
