import socket
import threading
import logging
import time
import queue
import sys 
     
MAX_SIZE_QUEUE_HEARTBEAT = 5
INTERVAL_HEARTBEAT = 3.0
TIMEOUT_LEADER_RESPONSE = 7.0 # TIME_FOR_PING_FROM_LEADER + 1
EXIT = "Exit"

class HeartbeatClient:

    def __init__(self, my_hostname: str, my_service_name: int):
        self.my_service_name = my_service_name
        self.my_hostname = my_hostname
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.my_hostname, self.my_service_name))
        self.socket.settimeout(TIMEOUT_LEADER_RESPONSE)
        self.joins = []
        self.queue = queue.Queue(maxsize =MAX_SIZE_QUEUE_HEARTBEAT)
        self.leader_hostname = None
        self.leader_service_name = None
        self.last_hearbeat_time = time.time()
        self.close_receiver = False
        self.close_sender = False

    def leader_had_timeout(self):
        if time.time() - self.last_hearbeat_time > TIMEOUT_LEADER_RESPONSE:
            logging.info(f"[{self.my_service_name}] Leader is fall! 😢")
            self.leader_hostname = None
            self.leader_service_name = None
            return True
        return False

    def sender(self):
        while True:
            try:
                if not self.leader_hostname or not self.leader_service_name:
                    logging.info(f"[{self.my_service_name}] Waiting for the leader! ⌛")
                    result = self.queue.get()
                    if result == EXIT:
                        logging.info("Sender finish by queue")
                        return
                    self.last_hearbeat_time = time.time()
                if self.leader_had_timeout():
                    continue
                message = "ping".encode('utf-8')
                self.socket.sendto(message, (self.leader_hostname, self.leader_service_name))
                time.sleep(INTERVAL_HEARTBEAT)
            except OSError as e:
                logging.info("Sender closed by socket was closed")
                return

    def handler_message(self, message, addr: list[str]):
        message = message.decode('utf-8')
        if "hi" in message:
            hi, leader_hostname = message.split("|")
            self.leader_hostname = leader_hostname
            self.leader_service_name = addr[1]
            self.queue.put("Lestgo!")
            logging.info(f"Leader found! 🎉 {self.leader_hostname} {self.leader_service_name}")
        elif message == "ping":
            logging.info(f"Ping received! 🏓 From leaader {self.leader_hostname} | {self.leader_service_name}")
            self.last_hearbeat_time = time.time()

    def receiver(self):
        while True:
            try: 
                data, addr = self.socket.recvfrom(1024)
                self.handler_message(data, addr)
            except socket.timeout:
                logging.info("Socket timeout! in receiver")
                if self.close_receiver:
                    return
                continue
            except OSError as e:
                return

    def run(self):
        thread_sender = threading.Thread(target= self.sender)
        thread_receiver = threading.Thread(target= self.receiver)
        self.joins.append(thread_sender)
        self.joins.append(thread_receiver)
        thread_sender.start()
        thread_receiver.start()
        
    def release_resources(self):
        logging.info("Tryting to release resource! ")
        self.close_receiver = True
        self.close_sender = True
        self.queue.put(EXIT)
        self.socket.close()
        for a_join in self.joins:
            a_join.join()   
        logging.info("All resources released 💯")

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')
    heartbeat = HeartbeatClient(f"127.0.0.{sys.argv[1]}",20015)
    logging.info(f"{heartbeat.my_hostname} {heartbeat.my_service_name} -{sys.argv[1]}-")
    thr_beat = threading.Thread(target=heartbeat.run)
    thr_beat.start()
    while True:
        a_input = input("Ingresq q para salir")
        if a_input == "q":
            heartbeat.release_resources()
            thr_beat.join()
            return



main()


""" 
import socket

server_address = ('127.0.0.1', 9010)

def socket_udp():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.connect(server_address)
    client_socket.send(b"ping")
    client_socket.settimeout(3)
    try: 
        message = client_socket.recv(1024)
        print(message)
    except socket.timeout:
        print("Timeout ⌚⌚⌚⌚")
    except ConnectionRefusedError as e:
        print(f"Node is fall! 👉👉{e}")
    finally:
        client_socket.close()

def main():
    socket_udp()

main()

"""