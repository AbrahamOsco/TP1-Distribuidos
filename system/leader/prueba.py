import signal
import time
import threading
import socket
import logging


def send_with_timeout():
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    skt.settimeout(1)
    try:
        skt.sendto("ping".encode('utf-8'), ('google.com', 5000))
    except socket.timeout:
        print("Timeout")


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',)
    send_with_timeout()    

main()

