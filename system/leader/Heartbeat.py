import socket
import threading
import logging
import time
import queue

MAX_SIZE_QUEUE_HEARTBEAT = 5
INTERVAL_HEARTBEAT = 3.0
TIMEOUT_LEADER_RESPONSE = 6.0

class Heartbeat:
    def __init__(self, my_hostname:str,  my_port: int):
        self.my_port = my_port
        self.my_hostname = my_hostname
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.my_hostname, self.my_port))
        self.joins = []
        self.queue = queue.Queue(maxsize =MAX_SIZE_QUEUE_HEARTBEAT)
        self.leader_hostname = None
        self.leader_servicename = None
        self.last_hearbeat_time = time.time()

    def sender(self):
        while True:
            if not self.leader_hostname or not self.leader_servicename:
                logging.info(f"[{self.my_port}] Waiting for the leader! ⌚")
                result = self.queue.get()
                logging.info(f"result: {result}")
                self.last_hearbeat_time = time.time()
            message = "ping".encode('utf-8')

            if time.time() - self.last_hearbeat_time > TIMEOUT_LEADER_RESPONSE:
                logging.info(f"[{self.my_port}] Leader is fall! 😢")
                self.leader_hostname = None
                self.leader_servicename = None
                continue
            
            self.socket.sendto(message, (self.leader_hostname, self.leader_servicename))
            time.sleep(INTERVAL_HEARTBEAT)
            
    def receiver(self):
        while True:
            data, addr = self.socket.recvfrom(1024)
            data = data.decode('utf-8')
            if "hi" in data:
                hi, leader_hostname = data.split("|")
                self.leader_hostname = leader_hostname
                self.leader_servicename = addr[1]
                self.queue.put("Lestgo!")
            elif data == "ping":
                self.last_hearbeat_time = time.time()
                continue
            else: 
                logging.info(f"[{self.my_port}] Recv a unknown message! {data}")

    def run(self):
        thread_sender = threading.Thread(target= self.sender)
        thread_receiver = threading.Thread(target= self.receiver)
        self.joins.append(thread_sender)
        self.joins.append(thread_receiver)
        thread_sender.start()
        thread_receiver.start()
        
    def release_resources(self):
        self.socket.close()
        for a_join in self.joins:
            a_join.join()   
        logging.info(f"[Hearbeat] All resources released 💯")
