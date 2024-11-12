from system.commonsSystem.utils.log import initialize_config_log 
from common.socket.Socket import Socket
from common.protocol.Protocol import Protocol
import threading
import os
import logging
import time
def get_service_name(id: int):
    return int(f"20{id}")

def get_host_name(id: int):
    return f"node{id-100}"

class LeaderElection:
    def __init__(self):
        self.joins = []
        self.id = int(os.getenv("NODE_ID"))
        self.leader_id = None
        self.ring_size = int(os.getenv("RING_SIZE"))
        self.config_params = initialize_config_log()
        self.hostname = get_host_name(self.id)
        self.service_name = get_service_name(self.id)
        self.next_id = self.getNextId(self.id) 
        self.skt_accept = Socket(port = self.service_name) # ej: puerto 20100 para el nodo 100
        self.skt_peer = None #socket Anterior
        self.skt_connect = Socket(ip= get_host_name(self.next_id) ,port = get_service_name(self.next_id)) # socket sgt
        self.protocol_connect = None
        self.protocol_peer = None
    
    def am_i_leader(self):
        return self.id == self.leader_id
    
    def thread_accepter(self):
        while True:
            skt_peer, addr = self.skt_accept.accept_simple()
            if not skt_peer:
                logging.error(f"action: accept | result: fail ❌ | ")
            else:
                logging.info(f"action: accept | result: success ✅ ")
                thr_client = threading.Thread(target =self.thread_client, args=(skt_peer, ))
                thr_client.start()
                self.joins.append(thr_client)
    
    def getNextId(self, aId: int):
        return ((aId - 100 + 1) % self.ring_size) + 100

    def show_my_info(self):
        logging.info(f"Id: {self.id} | NextId: {self.next_id} |" +
                     f"HostName: {self.hostname} | ServiceName: {self.service_name}")
    
    def start_election(self):
        logging.info("action: start_election")
        self.leader_id = None
        message :str = self.ids_to_msg("ELECTION", [self.id])
        self.safe_send_next(message, self.id)

    def safe_send_next(self, message: str, id: int):
        if id == self.next_id:
            logging.info("action: safe_send_next | message: mssg dio toda la vuelta! | result: success  ✅")
        else:
            logging.info(f"action: safe_send_next | message: {message} id: {id} | result: success  ✅")

    def ids_to_msg(self, message: str, ids: list[int]):
        return message + "|" + f"{len(ids)}" + "|" + "|".join([str(x) for x in ids])

    def run(self):
        self.show_my_info()
        thr_accepter = threading.Thread(target=self.thread_accepter)
        thr_accepter.start()
        self.joins.append(thr_accepter)
        canConnect, msg = self.skt_connect.connect()
        if not canConnect:
            logging.error(f"action: connect | result: fail ❌ | error: {msg}")
        else:
            logging.info(f"action: connect | result: success ✅")
            self.protocol_connect = Protocol(self.skt_connect)
            self.protocol_connect.send_string(f"HELLO From {self.id} to {self.next_id}")
        
    def thread_client(self, skt_peer):
        self.skt_peer = skt_peer
        self.protocol_peer = Protocol(self.skt_peer)
        thr_receiver = threading.Thread(target= self.thread_receiver_peer)
        thr_receiver.start()
        self.joins.append(thr_receiver)
        logging.info(f"action: Connect {self.id} and {self.next_id} ({get_host_name(self.next_id)})")


    # Peer solo recibe mensajes, del nodo anterior Ej peer de un nodo 2, recibe mensajes del nodo 1. 
    def thread_receiver_peer(self): 
        try:
            while True:
                message = self.protocol_peer.recv_string()
                logging.info(f"action: recv_string from Peer | message: {message} | result: success ✅")
        except Exception as e:
            logging.error(f"action: recv_string from Peer | result: fail ❌ | error: {e}")

    def sender(self, message: str):
        try:
            self.protocol_connect.send_string(message)
            logging.info(f"action: send_string | message: {message} | result: success ✅")
        except Exception as e:
            logging.error(f"action: send_string | result: fail ❌ | error: {e}")
    
    def release_resources(self):
        for thr in self.joins:
            thr.join()
        if self.skt_accept:
            self.skt_accept.close()
        if self.skt_connect:
            self.skt_connect.close()
        if self.skt_peer:
            self.skt_peer.close()
        