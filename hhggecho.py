from gevent.monkey import patch_all; patch_all()

import logging
import socket
import threading
import time
from os import environ
from os import getpid

PREAMBLE = (
    b"HTTP/1.1 200 OK\r\n"
    b"Content-Type: text/plain; charset=UTF-8\r\n"
    b"Connection: close\r\n"
    b"\r\n"
)
TOO_SLOW = (
    b"HTTP/1.1 408 Request Timeout\r\n"
    b"Connection: close\r\n"
    b"\r\n"
)

DELAY = 0.1

def main():
    assert int(environ["LISTEN_PID"]) == getpid()
    assert int(environ["LISTEN_FDS"]) == 1
    actual_listen_fds_socket = 3

    # Set socket, which is the only useful thing that TCPServer.__init__ does:
    listen_sock = socket.fromfd(actual_listen_fds_socket, socket.AF_INET, socket.SOCK_STREAM)
    while True:
        listen_sock.listen(1)
        conn, addr = listen_sock.accept()
        conn.settimeout(DELAY*2)
        threading.Thread(target=one_req, args=(conn, addr)).start()

def one_req(conn, addr):
    with conn:
        logging.info('Connected by %r', addr)
        time.sleep(DELAY)
        try:
            data = conn.recv((4*1024) - len(PREAMBLE))
        except TimeoutError:
            conn.sendall(TOO_SLOW)
        else:
            conn.sendall(PREAMBLE + data)


if __name__=="__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting")
    main()
