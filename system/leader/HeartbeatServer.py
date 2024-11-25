import csv
import os
from system.commonsSystem.utils.connectionLeader import OFFSET_MEDIC_HOSTNAME, get_service_name
from enum import Enum
import logging
import socket
import logging
import time
import threading
import subprocess

OFFSET_PORT_LEADER_MEDIC= 300
MAX_SIZE_QUEUE_HEARTBEAT = 1
TIME_NORMAL_FOR_SEND_PING = 3.0
THRESHOLD_RESTART_PING = 1.5
TIMEOUT_FOR_RECV_PING = 0.9 # INTERVAL_HEARBEAT + 1
TIME_TO_CHECK_FOR_DEAD_NODES = 0.9 #ASOCIATED WITH INTERVAL_HEARTBEAT TOO.

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
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(TIMEOUT_FOR_RECV_PING)
        self.socket.bind((self.my_hostname, self.my_service_name))
        self.nodes = []
        self.load_nodes()
    
    def load_nodes(self):
        csv_path = os.path.join(os.path.dirname(__file__), 'node_info.csv')
        try:
            with open(csv_path, 'r') as csvfile:
                csv_reader = csv.reader(csvfile)
                for row in csv_reader:
                    hostname = row[0].strip()
                    service_name = get_service_name(int(row[1]))
                    node_info = NodeInfo(hostname, service_name)
                    if "medic" in hostname:
                        node_info = NodeInfo(hostname, get_service_name(OFFSET_MEDIC_HOSTNAME + int(hostname[-1])))
                    self.nodes.append(node_info)
        except FileNotFoundError:
            logging.error(f"Node info CSV file not found at {csv_path}")
        except Exception as e:
            logging.error(f"Error reading node info CSV: {e}")
   
    def broadcast(self, message: bytes):
        for node in self.nodes:
            hostname_to_send = node.hostname
            if (node.numeric_ip is not None):
                hostname_to_send = node.numeric_ip
            send_messg = False
            if self.my_hostname == node.hostname:
                continue
            try:
                if node.status == NodeStatus.ACTIVE:
                    self.socket.sendto(message, (hostname_to_send, node.service_name))
                    send_messg = True
                elif node.status == NodeStatus.RECENTLY_REVIVED:
                    hi_message = f"hi|{self.my_hostname}".encode('utf-8')
                    self.socket.sendto(hi_message, (hostname_to_send, node.service_name))
                    self.socket.sendto(message, (hostname_to_send, node.service_name))
                    node.status = NodeStatus.ACTIVE
                    send_messg = True
            except socket.gaierror as e:
                node.status = NodeStatus.DEAD
                logging.info(f"We try to send a message a {node.hostname} but his is dead ⚰️ 🫥 🦾")
            if not send_messg:
                logging.info(f"Message {message} To {node.hostname} was not sent because his dead 💀")

    def send_hi(self):
        first_message = f"hi|{self.my_hostname}".encode('utf-8')
        self.broadcast(first_message)
        logging.info(f"Sent first Hi to all nodes 🏅✅")
    
    def sender(self):
        pass
        self.send_hi()
        while not self.socket._closed:
            try:
                time_to_sleep = TIME_NORMAL_FOR_SEND_PING
                message = "ping".encode('utf-8')
                start_time = time.time()
                self.broadcast(message)
                end_time = time.time()
                if end_time - start_time >= THRESHOLD_RESTART_PING: #Si supera 1.5s muy probable murio otro nodo y fue revivido necesitamos enviarle ping. con la data del lider
                    logging.info(f"Threshold exceed We send ping right now {end_time - start_time} 👌")
                    time_to_sleep = 0
                logging.debug(f"[⛑️ ] Sent ping to all Nodes! 💯🎯🎯🎯🎯")
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
                    self.update_lastime(addr, time_received) #si no recibo el ping de un nodo dead, su lastime no se actualiza. 
            except socket.timeout:
                logging.info("[⛑️ ] Don't recived any ping! ⌛")
            except OSError as e:
                logging.info("Receiver closed by socket was closed")
                return
    
    def revive_node(self, node: NodeInfo, initial=None):
        result = subprocess.run(['docker', 'start', f'{node.hostname}' ], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0 and not initial:
            logging.info(f"Revive {node.hostname} was success! 👼✅")
        elif result.returncode != 0: 
            logging.info(f"Revive {node.hostname} was failed! 😱❌")
        if initial:
            node.status = NodeStatus.ACTIVE
            return
        node.status = NodeStatus.RECENTLY_REVIVED

    def monitor_nodes(self):
        while not self.socket._closed:
            for node in self.nodes:
                if node.hostname == self.my_hostname:
                    continue
                elif node.last_time is None:
                    self.revive_node(node, initial=True) #Al inicio revivimos a todos ya sea q esta vivo o muerto.
                    logging.info(f"[⛑️ ] Node {node.hostname} First time 🆕 ")
                    node.last_time = time.time()
                elif time.time() - node.last_time > TIMEOUT_FOR_RECV_PING and node.status != NodeStatus.RECENTLY_REVIVED:
                    logging.info(f"[⛑️ ] Node {node.hostname} is dead! 💀 Now to Revive!")
                    self.revive_node(node)
                elif time.time() - node.last_time < TIMEOUT_FOR_RECV_PING:
                    logging.debug(f"[⛑️ ] 🫀 From: {node.hostname} ✅ ")
            time.sleep(TIME_TO_CHECK_FOR_DEAD_NODES)
            
    def run(self):
        thr_sender = threading.Thread(target= self.sender)
        thr_receiver = threading.Thread(target= self.receiver)
        thr_monitor = threading.Thread(target= self.monitor_nodes)
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

