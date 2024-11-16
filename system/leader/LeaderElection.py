from system.commonsSystem.utils.log import initialize_config_log
from system.leader.common_leader import get_host_name_medic, get_service_name, ids_to_msg, OFF_SET_MEDIC
from common.socket.Socket import Socket
from common.protocol.Protocol import Protocol
from system.leader.ControlValue import ControlValue 
from system.leader.InternalMedicServer import InternalMedicServer 
from system.leader.InternalMedicCheck import InternalMedicCheck 
from system.leader.HeartbeatClient import HeartbeatClient
from system.leader.HeartbeatServer import HeartbeatServer

import traceback
import threading
import os
import logging
import time
import queue
import signal

MESSG_COORD = "COORDINATOR"
MESSG_ACK = "ACK"
MESSG_ELEC = "ELECTION"
TIME_OUT_TO_FIND_LEADER = 5
TIME_OUT_TO_GET_ACK = 5
MAX_SIZE_QUEUE_PROTO_CONNECT = 5

class LeaderElection:
    def __init__(self):
        signal.signal(signal.SIGTERM, self.sign_term_handler)
        self.config_params = initialize_config_log()
        self.joins = []
        self.heartbeat_client = None
        self.heartbeat_server = None
        self.id = int(os.getenv("NODE_ID"))
        self.ring_size = int(os.getenv("RING_SIZE"))
        self.queue_proto_connect = queue.Queue(maxsize =MAX_SIZE_QUEUE_PROTO_CONNECT)
        self.send_connect_control = threading.Lock()
        self.send_peer_control = threading.Lock()
        self.leader_id = ControlValue(-1)
        self.got_ack = ControlValue(-1)
        self.stop_value = ControlValue(False)
        self.reset_skts_and_protocols()
        self.resource_control = threading.Lock()
       
    def thread_accepter(self):
        self.skt_accept = Socket(port = get_service_name(self.id))
        while True:
            skt_peer, addr = self.skt_accept.accept_simple()
            if not skt_peer:
                break
            else:
                thr_client = threading.Thread(target =self.thread_client, args=(skt_peer, ))
                thr_client.start()
                self.joins.append(thr_client)
    
    def start_hearbeat(self):
        self.heartbeat_client = HeartbeatClient(get_host_name_medic(self.id), get_service_name(self.id))
        self.heartbeat_client.run()
    
    def find_new_leader(self):
        self.release_resources()
        self.start_hearbeat()
        self.start_medic_server()
        self.start_accept()
        if self.stop_value.is_this_value(True):
            return
        logging.info(f"[{self.id}] Searching a leader!")
        self.leader_id.change_value(None)
        message = ids_to_msg(MESSG_ELEC, [self.id])
        start_time = time.time()
        self.safe_send_next(message, self.id)
        while True:
            with self.leader_id.condition:
                result_leader = self.leader_id.condition.wait_for(
                    lambda: not self.leader_id.is_this_value(None), TIME_OUT_TO_FIND_LEADER)
                if result_leader:
                    break
                elif (time.time() - start_time) >= TIME_OUT_TO_FIND_LEADER:
                    logging.info(f"[{self.id}] Timeout to find a leader!")
                break
        if self.leader_id.is_this_value(self.id):
            logging.info(f"[{self.id}⛑️] I'm the leader medic! 🎉 ")
            self.heartbeat_server = HeartbeatServer(get_host_name_medic(self.id), get_service_name(self.id))
            self.heartbeat_server.run()
        logging.info(f"[{self.id}] Finish new Leader 🪜🗡️ Now the leader is {self.leader_id.value}")
        


    def send_message_proto_connect_with_lock(self, message: str, next_id:int = -1):
        with self.send_connect_control:
            self.protocol_connect.send_string(message)
            if (next_id != -1):
                logging.info(f"[{self.id}-Connect] Send: {message} to: {next_id}")
            else:
                logging.info(f"[{self.id}-Connect] Send: {message}")

    def election_message_handler(self, ids_recv: list[int]):
        if self.id in ids_recv:
            leader_id = max(ids_recv)
            message_to_send = ids_to_msg(MESSG_COORD, [leader_id, self.id])
            self.send_message_proto_connect_with_lock(message_to_send)
        else:
            ids_recv.append(self.id)
            message_to_send = ids_to_msg(MESSG_ELEC, ids_recv)
            thr_continue_election = threading.Thread(target= self.safe_send_next, args=(message_to_send, self.id,))
            thr_continue_election.start()
            self.joins.append(thr_continue_election)
        message_to_send = ids_to_msg(MESSG_ACK, [self.id])
        self.send_message_proto_peer_with_lock(message_to_send)
    
    def coordinator_message_handler(self, ids_recv: list[int]):
        self.leader_id.change_value(ids_recv[0])
        self.leader_id.notify_all()
        if self.id not in ids_recv:
            ids_recv.append(self.id)
            message_to_send = ids_to_msg(MESSG_COORD, ids_recv)
            thr_continue_coord = threading.Thread(target= self.safe_send_next, args=(message_to_send, self.id, ))
            thr_continue_coord.start()
            self.joins.append(thr_continue_coord)
        message_to_send = ids_to_msg(MESSG_ACK, [self.id])
        self.send_message_proto_peer_with_lock(message_to_send)

    def thread_receiver_connect(self):
        while True:
            try:
                message_recv = self.protocol_connect.recv_string()
                logging.info(f"[{self.id}-Connect] Recv: {message_recv} 🎃")
                message_type, ids_recv = self.parse_message(message_recv)
                if (message_type == MESSG_ACK):
                    self.ack_message_handler(ids_recv[0])
            except Exception as e :
                if self.skt_connect and self.skt_connect.is_closed():
                    break
                break
        
    def send_message_and_wait_for_ack(self, message: str, next_id: int, ):
        self.send_message_proto_connect_with_lock(message, next_id)
        start_time = time.time()
        while True:
            with self.got_ack.condition:
                result = self.got_ack.condition.wait_for(lambda: self.condition_to_get_ack(next_id), TIME_OUT_TO_GET_ACK)
                if result:
                    break
                elif (time.time() - start_time) >= TIME_OUT_TO_GET_ACK:
                    logging.info(f"[{self.id}] Connect Timeout to get a ack! from {next_id} We try with the next!")
                    if self.leader_id is not None:
                        logging.info(f"[{self.id}] We found a leader already! Leader:{self.leader_id.value} 💯")
                        break
                    with self.resource_control:
                        if self.skt_connect and self.skt_connect.was_closed:
                            self.skt_connect.close()
                    self.skt_connect = None
                    self.protocol_connect = None
                    self.safe_send_next(message, next_id)

    def connect_and_send_message(self, next_id: int, message: str):
        self.skt_connect = Socket(ip= get_host_name_medic(next_id), port= get_service_name(next_id))
        can_connect, msg = self.skt_connect.connect() 
        if can_connect:
            self.protocol_connect = Protocol(self.skt_connect)
            self.queue_proto_connect.put("ProtoConnect Created successfully ✅ 🌟")
            thr_receiver_connect = threading.Thread(target= self.thread_receiver_connect)
            thr_receiver_connect.start()
            self.joins.append(thr_receiver_connect)
            self.send_message_and_wait_for_ack(message, next_id)
        return can_connect        

    def safe_send_next(self, message: str, a_id: int):
        if not self.leader_id.is_this_value(None): # Si encontre un lider ya no enviemos mensajes. 
            return
        next_id = self.getNextId(a_id)
        if a_id == next_id:
            logging.info(f"action: safe_send_next | message: mssg dio toda la vuelta! | result: success  ❌")
            raise Exception("Di toda la vuelta sin ninguna respuestas!")
        self.got_ack.change_value(None)
        if self.skt_connect and self.protocol_connect:
            self.send_message_and_wait_for_ack(message, next_id)
        else:
            while True:
                logging.info(f"[{self.id}] Trying to connect to {next_id} 🔄")
                if InternalMedicCheck.is_alive(self.id, next_id):
                    self.connect_and_send_message(next_id, message)
                    break
                else:
                    logging.info(f"[{self.id}] We can't connect to {next_id}  ❌")
                    next_id = self.getNextId(next_id)
        
    def get_message(self):
        message_recv = self.protocol_peer.recv_string()
        logging.info(f"[{self.id}-Peer] Recv: {message_recv} 🎃")
        return self.parse_message(message_recv)

    def thread_receiver_peer(self):
        result = self.queue_proto_connect.get()
        while True:
            try: 
                if self.stop_value.is_this_value(True):
                    break
                message_type, ids_recv = self.get_message()
                if (message_type == MESSG_ACK):
                    self.ack_message_handler(ids_recv[0])
                elif (message_type == MESSG_ELEC):
                    self.election_message_handler(ids_recv)
                elif (message_type == MESSG_COORD):
                    self.coordinator_message_handler(ids_recv)
            except Exception as e:
                if self.skt_peer and self.skt_peer.is_closed():
                    break
                #traceback.print_exc()  # Imprime la traza completa del error
                break
        self.stop_value.change_value(False)
        self.stop_value.notify_all()

    def thread_client(self, skt_peer):
        self.skt_peer = skt_peer
        self.protocol_peer = Protocol(self.skt_peer)
        thr_receiver = threading.Thread(target= self.thread_receiver_peer)
        thr_receiver.start()
        self.joins.append(thr_receiver)
    
    # Utils functions
    def stop(self):
        self.stop_value.change_value(True)
        self.stop_value.notify_all()
        self.release_resources()

    def getNextId(self, aId: int):
        return ((aId - OFF_SET_MEDIC + 1) % self.ring_size) + OFF_SET_MEDIC

    def send_message_proto_peer_with_lock(self, message: str):
        with self.send_peer_control:
            self.protocol_peer.send_string(message)
            logging.info(f"[{self.id}-Peer]  Send: {message}")

    def condition_to_get_ack(self, next_id :int):
        return self.got_ack.is_this_value(next_id)

    def ack_message_handler(self, ack_value:int):
        self.got_ack.change_value(ack_value)
        self.got_ack.notify_all()

    def start_accept(self):
        thr_accepter = threading.Thread(target=self.thread_accepter)
        thr_accepter.start()
        self.joins.append(thr_accepter)

    def parse_message(self, message: str):
        fields = message.split("|")
        return (fields[0], [int(x) for x in fields[1:]])

    def start_medic_server(self):
        self.medic_server = InternalMedicServer(self.id)
        thr_medic_server = threading.Thread(target=self.medic_server.run)
        thr_medic_server.start()
        self.joins.append(thr_medic_server)

    def reset_skts_and_protocols(self):
        self.medic_server = None
        self.skt_accept = None # ej: puerto 20100 para el nodo 100
        self.skt_peer = None #socket Anterior
        self.skt_connect = None # socket sgt
        self.protocol_connect = None
        self.protocol_peer = None

    def sign_term_handler(self, signum, frame):
        logging.info(f"action: ⚡ Signal Handler | signal: {signum} | result: success ✅")
        self.release_resources()

    def am_i_leader(self):
        return self.leader_id.is_this_value(self.id)

    def get_leader_id(self):
        return self.leader_id.value
    
    def release_threads(self):
        for thr in self.joins:
            if thr.is_alive():
                thr.join()
        self.joins.clear()

    def release_resources(self):
        with self.resource_control:
            if self.skt_connect:
                self.skt_connect.close()
        if self.heartbeat_server:
            self.heartbeat_server.release_resources()
            self.heartbeat_server = None
        if self.medic_server:
            self.medic_server.release_resources()
        if self.skt_accept:
            self.skt_accept.close()
        if self.skt_peer:
            self.skt_peer.close()
        if self.heartbeat_client:
            self.heartbeat_client.release_resources()
            self.heartbeat_client = None
        self.reset_skts_and_protocols()
        self.release_threads()
        logging.info(f"All resource are free in LeaderElection 💯")