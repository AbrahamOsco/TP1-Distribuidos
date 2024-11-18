from system.commonsSystem.utils.connectionLeader import OFFSET_MEDIC_HOSTNAME, get_service_name
from system.leader.InternalMedicCheck import InternalMedicCheck

from enum import Enum
import logging
import socket
import logging
import time
import threading
import subprocess

OFFSET_PORT_LEADER_MEDIC= 300
MAX_SIZE_QUEUE_HEARTBEAT = 5
TIME_NORMAL_FOR_SEND_PING = 3.0
THRESHOLD_RESTART_PING = 1.5
TIMEOUT_FOR_RECV_PING = 1.5 # INTERVAL_HEARBEAT + 1
TIME_TO_CHECK_FOR_DEAD_NODES = 1.0 #ASOCIATED WITH INTERVAL_HEARTBEAT TOO.

class NodeStatus(Enum):
    ACTIVE = 0
    DEAD = 1
    RECENTLY_REVIVED = 2


class NodeInfo:
    def __init__(self, hostname: str, service_name: int):
        self.hostname = hostname
        self.numeric_ip = None
        self.service_name = service_name
        self.last_time = None
        self.status = NodeStatus.ACTIVE
        self.active = True
        self.counter_loading = 0

    def update_lastime(self, time_received):
        self.last_time = time_received

class HeartbeatServer:
    def __init__(self,my_hostname, my_service_name):
        self.joins = []
        self.my_hostname = my_hostname
        self.my_service_name = my_service_name + OFFSET_PORT_LEADER_MEDIC
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(TIMEOUT_FOR_RECV_PING)
        self.socket.bind((self.my_hostname, self.my_service_name))
        self.nodes = []
        self.load_nodes()
    
    def load_nodes(self):
        self.nodes.append(NodeInfo("medic_0", get_service_name(OFFSET_MEDIC_HOSTNAME)))
        self.nodes.append(NodeInfo("medic_1", get_service_name(OFFSET_MEDIC_HOSTNAME + 1)))        
        self.nodes.append(NodeInfo("medic_2", get_service_name(OFFSET_MEDIC_HOSTNAME + 2)))        
        self.nodes.append(NodeInfo("medic_3", get_service_name(OFFSET_MEDIC_HOSTNAME + 3)))
        self.nodes.append(NodeInfo("filterbasic_0", get_service_name(100)))
        self.nodes.append(NodeInfo("filterbasic_1", get_service_name(101)))
        self.nodes.append(NodeInfo("filterbasic_2", get_service_name(102)))
        self.nodes.append(NodeInfo("filterbasic_3", get_service_name(103)))
        self.nodes.append(NodeInfo("nodetoy_0", get_service_name(104)))
        self.nodes.append(NodeInfo("nodetoy_1", get_service_name(105)))
        self.nodes.append(NodeInfo("nodetoy_2", get_service_name(106)))
        self.nodes.append(NodeInfo("nodetoy_3", get_service_name(107)))

    # Es raro si el nodo muere y lo detectamos ya sea en el excepcion o al monitorearlo hay q setearlo q no esta activo. 
    # porque si tratamos de enviar otro mensaje a un nodo muerto, tarda mucho mas el docker.   
    def broadcast(self, message: bytes):
        for node in self.nodes:
            send_messg = False
            try:
                if self.my_hostname != node.hostname and node.status == NodeStatus.ACTIVE:
                    self.socket.sendto(message, (node.hostname, node.service_name))
                    send_messg = True
                elif self.my_hostname != node.hostname and node.status == NodeStatus.RECENTLY_REVIVED:
                    hi_message = f"hi|{self.my_hostname}".encode('utf-8')
                    self.socket.sendto(hi_message, (node.hostname, node.service_name))
                    self.socket.sendto(message, (node.hostname, node.service_name))
                    node.status = NodeStatus.ACTIVE
                    send_messg = True
            except socket.gaierror as e:
                node.status = NodeStatus.DEAD
                logging.info(f"We try to send a message a {node.hostname} but is dead ⚰️ 🫥 🦾")
            if not send_messg and self.my_hostname != node.hostname:
                logging.info(f"Message {message} To {node.hostname} was not sent because his dead 💀")

    def send_hi(self):
        first_message = f"hi|{self.my_hostname}".encode('utf-8')
        self.broadcast(first_message)
    
    def sender(self):
        self.send_hi()
        while not self.socket._closed:
            try:
                time_to_sleep = TIME_NORMAL_FOR_SEND_PING
                message = "ping".encode('utf-8')
                start_time = time.time()
                self.broadcast(message)
                end_time = time.time()
                if end_time - start_time >= THRESHOLD_RESTART_PING: #Si supera 1.5s muy probable murio otro nodo y fue revivido necesitamos enviarle ping. con la data del lider
                    logging.info(f"Time to broadcast was {end_time - start_time}: go broadcast again. ⌛⌛")
                    time_to_sleep = 0
                logging.info(f"[⛑️ ] Sent ping to all Nodes! 💯🎯🎯🎯🎯")
                time.sleep(time_to_sleep)
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
                return

    def receiver(self):
        while not self.socket._closed:
            try:
                message, addr = self.socket.recvfrom(1024)
                time_received = time.time()
                message = message.decode('utf-8')
                if "|" in message:
                    self.add_real_ip(addr, message, time_received)
                elif "ping" in message:
                    self.update_lastime(addr, time_received)
            except socket.timeout:
                logging.info("[⛑️ ] Don't recived any ping! ⌛")
            except OSError as e:
                logging.info("Receiver closed by socket was closed")
                return
    
    def revive_node(self, node: NodeInfo):
        result = subprocess.run(['docker', 'start', f'{node.hostname}' ], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            logging.info(f"Revive {node.hostname} was success! 👼✅")
        else: 
            logging.info(f"Revive {node.hostname} was failed! 😱❌")
        node.status = NodeStatus.RECENTLY_REVIVED

    def monitor(self):
        while not self.socket._closed:
            for node in self.nodes:
                if node.hostname == self.my_hostname:
                    continue
                elif node.last_time is None:
                    logging.info(f"[⛑️ ] Node {node.hostname} Has a new LastTime ⌛")
                    node.last_time = time.time()
                elif time.time() - node.last_time > TIMEOUT_FOR_RECV_PING and node.status != NodeStatus.RECENTLY_REVIVED:
                    logging.info(f"[⛑️ ] Node {node.hostname} is dead! 💀 Now to Revive!")
                    node.status = NodeStatus.DEAD
                    self.revive_node(node)
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

    def free_resources(self):
        self.socket.close()
        for thr in self.joins:
            thr.join()
        logging.info("[Hearbet Server] All resources are free 💯")

