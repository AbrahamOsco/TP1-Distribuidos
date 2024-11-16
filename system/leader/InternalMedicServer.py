from system.leader.common_leader import get_service_name, OFF_SET_MEDIC
import threading
import socket
import logging

TIMEOUT_FOR_CHECK_PING = 1

class InternalMedicServer:
    def __init__(self, node_id: int):
        self.port = get_service_name(node_id + OFF_SET_MEDIC)
        self.node_id = node_id
        self.skt_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.skt_udp.bind(("", self.port))
        self.skt_udp.settimeout(TIMEOUT_FOR_CHECK_PING)
        self.joins = []
    
    def start(self):
        while not self.skt_udp._closed:
            try:
                message, addr = self.skt_udp.recvfrom(1024)
                if message == b"ping":
                    self.skt_udp.sendto(b"ping", addr)
                elif message == b'':
                    logging.info(f"[{self.node_id}] Received empty message, ignoring")
                    continue
                else:
                    logging.info(f"msg recv: {message} ❌")
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

    
    def free_resources(self):
        self.skt_udp.close()
        for thr in self.joins:
            thr.join()
        logging.info("[Internal MedicServer] All resources are free 💯")


