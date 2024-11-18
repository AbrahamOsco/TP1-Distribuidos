from system.leader.common_leader import OFFSET_MEDIC_SERVER_INTERN 
from system.commonsSystem.utils.connectionLeader import get_service_name
import threading
import socket
import logging

TIMEOUT_FOR_CHECK_PING = 1

class InternalMedicServer:

    def __init__(self, node_id: int):
        self.service_name = get_service_name(node_id + OFFSET_MEDIC_SERVER_INTERN)
        self.node_id = node_id
        self.skt_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.skt_udp.bind(("", self.service_name))
        self.skt_udp.settimeout(TIMEOUT_FOR_CHECK_PING)
        self.joins = []
        self.leader_id = None

    def start(self):
        while not self.skt_udp._closed:
            try:
                message, addr = self.skt_udp.recvfrom(1024)
                if message == b"ping":
                    self.skt_udp.sendto(b"ping", addr)
                elif message == b"leader_id":
                    if not self.leader_id:
                        self.skt_udp.sendto(b"no_leader", addr)
                    else:
                        leader_id_str = str(self.leader_id).encode('utf-8')
                        self.skt_udp.sendto(leader_id_str, addr)
            except socket.timeout:
                continue
            except Exception as e:
                if not self.skt_udp._closed:
                    logging.info(f"[{self.node_id}] Error in serverUDP 🗡️ ⚡")
                break

    def run(self):
        thr_medic_server = threading.Thread(target=self.start)
        self.joins.append(thr_medic_server)
        thr_medic_server.start()

    def set_leader_id(self, leader_id: int):
        self.leader_id = leader_id
    
    def free_resources(self):
        self.skt_udp.close()
        for thr in self.joins:
            thr.join()
        logging.info("[Internal MedicServer] All resources are free 💯")

