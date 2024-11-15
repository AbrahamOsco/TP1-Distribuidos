import socket
import logging
import time

MAX_SIZE_QUEUE_HEARTBEAT = 5
INTERVAL_HEARTBEAT = 3.0

def start_server_udp():
    a_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    a_socket.bind(("", 9010))
    first_time = False
    while True:
        if not first_time:
            first_message = "hi|127.0.0.1".encode('utf-8')
            a_socket.sendto(first_message, ("127.0.0.1", 20015))
            first_time = True
        data, addr = a_socket.recvfrom(1024)
        data = data.decode('utf-8')

        if "ping" in data:
            logging.info(f"[Leader] Hearbeat 🫀 from {addr} ✅ ")
            message_to_send = "ping".encode('utf-8')
            a_socket.sendto(message_to_send, addr)
        else:
            logging.info(f"Another message:{data} {addr}")

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')
    start_server_udp()

main()
