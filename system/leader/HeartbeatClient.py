import socket
import threading
import logging
import time
import queue

MAX_SIZE_QUEUE_HEARTBEAT = 5
TIME_FOR_SEND_PING = 3.0
TIMEOUT_LEADER_RESPONSE = 7.5
TIMEOUT_SOCKET = 2
EXIT = "Exit"
SPECIAL_PING ="special_ping"

class HeartbeatClient:

    def __init__(self, my_hostname: str,  my_service_name: int):
        self.my_service_name = my_service_name
        self.my_hostname = my_hostname
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.my_hostname, self.my_service_name))
        self.numeric_ip = socket.gethostbyname(socket.gethostname())
        self.socket.settimeout(TIMEOUT_SOCKET)
        self.joins = []
        self.queue = queue.Queue(maxsize =MAX_SIZE_QUEUE_HEARTBEAT)
        self.leader_hostname = None
        self.leader_service_name = None
        self.last_hearbeat_time = time.time()

    def leader_had_timeout(self):
        if time.time() - self.last_hearbeat_time > TIMEOUT_LEADER_RESPONSE:
            logging.info(f"[{self.my_service_name}] Leader is fall! 😢")
            self.leader_hostname = None
            self.leader_service_name = None
            return True
        return False

    def sender(self):
        while not self.socket._closed:
            try:
                if not self.leader_hostname or not self.leader_service_name:
                    logging.info(f"[{self.my_service_name}] Waiting for the leader! ⌚")
                    result = self.queue.get()
                    if result == SPECIAL_PING:
                        message = f"ping|{self.numeric_ip}".encode('utf-8')
                        self.socket.sendto(message, (self.leader_hostname, self.leader_service_name))
                        logging.info(f"Send special ping: ping|-{self.numeric_ip}-")
                    if result == EXIT:
                        logging.info("Sender finish by queue")
                        return
                    self.last_hearbeat_time = time.time()
                if self.leader_had_timeout():
                    continue
                message = "ping".encode('utf-8')
                self.socket.sendto(message, (self.leader_hostname, self.leader_service_name))
                time.sleep(TIME_FOR_SEND_PING)
            except OSError as e:
                logging.info("Sender closed by socket was closed")
                return

    def handler_message(self, message: bytes, addr: list[str]):
        if "hi" in message:
            hi, leader_hostname = message.split("|")
            self.leader_hostname = leader_hostname
            self.leader_service_name = addr[1]
            self.queue.put(SPECIAL_PING)
        elif message == "ping":
            self.last_hearbeat_time = time.time()

    def receiver(self):
        while not self.socket._closed:
            try: 
                data, addr = self.socket.recvfrom(1024)
                data = data.decode('utf-8')
                self.handler_message(data, addr)
            except socket.timeout:
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
        logging.info("[HeartClient] Tryting to release resource! ")
        self.socket.close()
        self.close_receiver = True
        self.close_sender = True
        self.queue.put(EXIT)
        for a_join in self.joins:
            a_join.join()   
        logging.info("[HeartClient]All resources are free 💯")

