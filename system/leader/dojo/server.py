import logging
import socket
import logging
import time
import threading

OFFSET_PORT_LEADER= 300
MAX_SIZE_QUEUE_HEARTBEAT = 5
TIME_FOR_PING_FROM_LEADER = 6.0 
TIMEOUT_FOR_RECV_PING = 4 # INTERVAL_HEARBEAT + 1
TIME_TO_CHECK_FOR_DEAD_NODES = 3.0
MEDIC_EMOJIS = "⛑️ 🇨🇭"

class NodeInfo:
    def __init__(self, hostname: str, service_name: int):
        self.hostname = hostname
        self.ip_numeric = None
        self.service_name = service_name
        self.last_time = None
    
    def update_lastime(self, time_received):
        self.last_time = time_received

class HeartbeatServer:
    def __init__(self, my_hostname, my_port):
        self.joins = []
        self.my_hostname = my_hostname
        self.my_port = my_port + OFFSET_PORT_LEADER
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(TIMEOUT_FOR_RECV_PING)
        self.socket.bind((my_hostname, my_port))
        self.nodes = []
        self.load_nodes()
    
    def load_nodes(self):
        self.nodes.append(NodeInfo("127.0.0.1", 20015))
        self.nodes.append(NodeInfo("127.0.0.2", 20015))        

    def broadcast(self, message:str):
        for node in self.nodes:
            self.socket.sendto(message, (node.hostname, node.service_name))

    def send_hi(self):
        first_message = f"hi|{self.my_hostname}".encode('utf-8')
        self.broadcast(first_message)

    def sender(self):
        self.send_hi()
        while True:
            try:
                message = "ping".encode('utf-8')
                self.broadcast(message)
                time.sleep(TIME_FOR_PING_FROM_LEADER)
            except OSError as e:
                logging.info("Sender closed by socket was closed")
                return
    def update_lastime(self, addr, last_time):
        for node in self.nodes:
            if node.hostname == addr[0] and node.service_name == addr[1]:
                node.update_lastime(last_time)
                return

    def receiver(self):
        while True:
            try:
                message, addr = self.socket.recvfrom(1024)
                time_received = time.time()
                message = message.decode('utf-8')
                if "ping" in message:
                    self.update_lastime(addr, time_received)
            except socket.timeout:
                logging.info("Timeout in HeartbeatServer ⏳")
                continue
            except OSError as e:
                logging.info("Receiver closed by socket was closed")
                return
    
    def monitor(self):
        while True:
            for node in self.nodes:
                if node.last_time is None:
                    logging.info(f"[Leader] Node {node.hostname} is Loading ⏳")
                elif time.time() - node.last_time > TIMEOUT_FOR_RECV_PING:
                    logging.info(f"[Leader] Node {node.hostname} is dead! 💀 Now to Revive!")
                elif time.time() - node.last_time < TIMEOUT_FOR_RECV_PING:
                    logging.info(f"[Leader] Hearbeat 🫀 from {node.hostname} {node.service_name} ✅ ")
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

    def free_resources(self):
        self.socket.close()
        for thr in self.joins:
            thr.join()
        logging.info("All resources are free 💯")

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')
    heartbeat_server = HeartbeatServer("127.0.0.2", 21000)
    heartbeat_server.run()
    while True:
        a_input = input("Ingresa q para salir")
        if a_input == "q":
            heartbeat_server.free_resources()
            return

main()
