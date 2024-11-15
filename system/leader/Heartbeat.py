import socket
import threading
import logging
import time
import queue

MAX_SIZE_QUEUE_HEARTBEAT = 5
INTERVAL_HEARTBEAT = 3.0
TIMEOUT_LEADER_RESPONSE = 5.0
TIMEOUT_SOCKET = 2
EXIT = "Exit"

class Heartbeat:
    def __init__(self, my_hostname:str,  my_port: int):
        self.my_port = my_port
        self.my_hostname = my_hostname
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(TIMEOUT_SOCKET)
        self.socket.bind((self.my_hostname, self.my_port))
        self.joins = []
        self.queue = queue.Queue(maxsize =MAX_SIZE_QUEUE_HEARTBEAT)
        self.leader_hostname = None
        self.leader_servicename = None
        self.last_hearbeat_time = time.time()
        self.close_receiver = False
        self.close_sender = False

    def leader_had_timeout(self):
        if time.time() - self.last_hearbeat_time > TIMEOUT_LEADER_RESPONSE:
            logging.info(f"[{self.my_port}] Leader is fall! 😢")
            self.leader_hostname = None
            self.leader_servicename = None
            return True
        return False

    def sender(self):
        while True:
            try:
                if not self.leader_hostname or not self.leader_servicename:
                    logging.info(f"[{self.my_port}] Waiting for the leader! ⌚")
                    result = self.queue.get()
                    if result == EXIT:
                        logging.info("Sender finish by queue")
                        return
                    self.last_hearbeat_time = time.time()
                if self.leader_had_timeout():
                    continue
                message = "ping".encode('utf-8')
                self.socket.sendto(message, (self.leader_hostname, self.leader_servicename))
                time.sleep(INTERVAL_HEARTBEAT)
            except OSError as e:
                logging.info("Sender closed by socket was closed")
                return

    def handler_message(self, message: bytes, addr: list[str]):
        if "hi" in message:
            hi, leader_hostname = message.split("|")
            self.leader_hostname = leader_hostname
            self.leader_servicename = addr[1]
            self.queue.put("Lestgo!")
        elif message == "ping":
            self.last_hearbeat_time = time.time()

    def receiver(self):
        while True:
            try: 
                data, addr = self.socket.recvfrom(1024)
                data = data.decode('utf-8')
                self.handler_message(data, addr)
            except socket.timeout:
                logging.info("Socket timeout! ⌚ in receiver")
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
        logging.info("All resources are free 💯")

