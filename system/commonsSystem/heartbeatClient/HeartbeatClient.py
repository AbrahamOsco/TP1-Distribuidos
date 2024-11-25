from system.commonsSystem.utils.connectionLeader import get_host_name, get_service_name
import socket
import threading
import logging
import time
import queue

MAX_SIZE_QUEUE_HEARTBEAT = 1
TIME_FOR_SEND_PING_HEARTBEAT = 0.45
TIMEOUT_LEADER_RESPONSE = 4
TIMEOUT_SOCKET = 2.0
EXIT = "Exit"
SPECIAL_PING ="special_ping"

class HeartbeatClient:

    def __init__(self, node_id: int):
        self.my_hostname = get_host_name(node_id)
        self.my_service_name = get_service_name(node_id)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.my_hostname, self.my_service_name))
        self.my_numeric_ip = socket.gethostbyname(socket.gethostname())
        self.socket.settimeout(TIMEOUT_SOCKET)
        self.joins = []
        self.queue = queue.Queue(maxsize =MAX_SIZE_QUEUE_HEARTBEAT)
        self.leader_hostname = None
        self.leader_numeric_ip = None
        self.leader_service_name = None
        self.last_hearbeat_time = time.time()
        self.special_ping = True

    def init_logg_info(self):
        logging.basicConfig(
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S',
        )

    def leader_had_timeout(self):
        if time.time() - self.last_hearbeat_time > TIMEOUT_LEADER_RESPONSE:
            logging.info(f"[{self.my_service_name}] Leader is dead! 💀")
            self.leader_hostname = None
            self.leader_service_name = None
            self.leader_numeric_ip = None
            return True
        return False

    def send_special_ping(self, result):
        if result == SPECIAL_PING:
            message = f"ping|{self.my_numeric_ip}".encode('utf-8')
            self.socket.sendto(message, (self.leader_numeric_ip, self.leader_service_name))

    def sender(self):
        while not self.socket._closed:
            try:
                if not self.leader_hostname or not self.leader_service_name or not self.queue.empty():
                    result = self.queue.get()
                    self.send_special_ping(result)
                    if result == EXIT:
                        return
                    self.last_hearbeat_time = time.time()
                if self.leader_had_timeout():
                    continue
                message = "ping".encode('utf-8')
                self.socket.sendto(message, (self.leader_numeric_ip, self.leader_service_name))
                time.sleep(TIME_FOR_SEND_PING_HEARTBEAT)
            except OSError as e:
                return

    def handler_message(self, message: bytes, addr: list[str]):
        if "hi" in message and self.leader_numeric_ip != addr[0]: #not self.leader_hostname
            hi, leader_hostname = message.split("|")
            self.leader_hostname = leader_hostname
            self.leader_numeric_ip = addr[0]
            self.leader_service_name = int(addr[1])
            self.queue.put(SPECIAL_PING)
        self.last_hearbeat_time = time.time()

    def receiver(self):
        while not self.socket._closed:
            try: 
                data, addr = self.socket.recvfrom(1024)
                data = data.decode('utf-8')
                logging.debug(f"Recv: {data} 👈 ✅")
                self.handler_message(data, addr)
            except socket.timeout:
                continue
            except OSError as e:
                return

    def run(self):
        self.init_logg_info()
        thread_sender = threading.Thread(target= self.sender)
        thread_receiver = threading.Thread(target= self.receiver)
        self.joins.append(thread_sender)
        self.joins.append(thread_receiver)
        thread_sender.start()
        thread_receiver.start()
        
    def free_resources(self):
        self.socket.close()
        self.queue.put(EXIT)
        for a_join in self.joins:
            a_join.join()   
        logging.info("[Heartbeat Client] All resources are free 💯")

