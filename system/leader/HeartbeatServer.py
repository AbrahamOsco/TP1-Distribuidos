import logging
import socket
import logging
import time
import threading

OFFSET_PORT_LEADER= 300
MAX_SIZE_QUEUE_HEARTBEAT = 5
TIME_FOR_SEND_PING = 6.0 
TIMEOUT_FOR_RECV_PING = 4 # INTERVAL_HEARBEAT + 1
TIME_TO_CHECK_FOR_DEAD_NODES = 3.0

class NodeInfo:
    def __init__(self, hostname: str, service_name: int):
        self.hostname = hostname
        self.numeric_ip = None
        self.service_name = service_name
        self.last_time = None
        self.active = True
    
    def update_lastime(self, time_received):
        self.last_time = time_received

class HeartbeatServer:
    def __init__(self, my_hostname, my_service_name):
        self.joins = []
        self.my_hostname = my_hostname
        self.my_service_name = my_service_name + OFFSET_PORT_LEADER
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(TIMEOUT_FOR_RECV_PING)
        self.socket.bind((self.my_hostname, self.my_service_name))
        self.nodes = []
        self.load_nodes()
    
    def load_nodes(self):
        self.nodes.append(NodeInfo("medic0", 20100))
        self.nodes.append(NodeInfo("medic1", 20101))        
        self.nodes.append(NodeInfo("medic2", 20102))        
        self.nodes.append(NodeInfo("medic3", 20103))        

    def broadcast(self, message: bytes):
        for node in self.nodes:
            if self.my_hostname != node.hostname and node.active:
                try:
                    self.socket.sendto(message, (node.hostname, node.service_name))
                except socket.gaierror as e:
                    node.active = False
                    logging.info(f"We try to send a message a {node.hostname} but is dead ⚰️ 🫥")

    def send_hi(self):
        first_message = f"hi|{self.my_hostname}".encode('utf-8')
        self.broadcast(first_message)

    def sender(self):
        self.send_hi()
        while not self.socket._closed:
            try:
                message = "ping".encode('utf-8')
                self.broadcast(message)
                logging.info(f"Sent ping to all Nodes! 💯🎯🎯🎯🎯")
                time.sleep(TIME_FOR_SEND_PING)
            except OSError as e:
                logging.info("Sender closed by socket was closed")
                return
    
    def update_lastime(self, addr, last_time):
        for node in self.nodes:
            if node.numeric_ip == addr[0] and node.service_name == addr[1]:
                node.update_lastime(last_time)
                return
    
    def add_real_ip(self, addr, message, last_time):
        for node in self.nodes:
            if node.service_name == addr[1]:
                node.numeric_ip = message.split("|")[1]
                node.update_lastime(last_time)
                logging.info(f"{node.hostname}| ip: {node.numeric_ip} port: {node.service_name} ✅")
                return

    def receiver(self):
        while not self.socket._closed:
            try:
                message, addr = self.socket.recvfrom(1024)
                time_received = time.time()
                message = message.decode('utf-8')
                #logging.info(f"[⛑️ ] Received message: {message} from {addr}")
                if "|" in message:
                    self.add_real_ip(addr, message, time_received)
                elif "ping" in message:
                    self.update_lastime(addr, time_received)
            except socket.timeout:
                logging.info("Timeout in HeartbeatServer ⏳")
                continue
            except OSError as e:
                logging.info("Receiver closed by socket was closed")
                return
    
    def monitor(self):
        while not self.socket._closed:
            for node in self.nodes:
                if node.hostname == self.my_hostname:
                    continue
                elif node.last_time is None:
                    logging.info(f"[⛑️ ] Node {node.hostname} is Loading ⏳")
                elif time.time() - node.last_time > TIMEOUT_FOR_RECV_PING:
                    logging.info(f"[⛑️ ] Node {node.hostname} is dead! 💀 Now to Revive!")
                elif time.time() - node.last_time < TIMEOUT_FOR_RECV_PING:
                    logging.info(f"[⛑️ ] 🫀 From: {node.hostname} ✅ ")
            time.sleep(TIME_TO_CHECK_FOR_DEAD_NODES)

    def run(self):
        thr_sender = threading.Thread(target= self.sender)
        thr_receiver = threading.Thread(target= self.receiver)
        thr_monitor = threading.Thread(target= self.monitor)
        self.joins.append(thr_monitor)
        self.joins.append(thr_sender)
        self.joins.append(thr_receiver)
        thr_sender.start()
        thr_receiver.start()
        thr_monitor.start()

    def release_resources(self):
        self.socket.close()
        logging.info("[Hearbet Server] Closing socket! 🍡")
        for thr in self.joins:
            thr.join()
        logging.info("[Hearbet Server] All resources are free 💯")

