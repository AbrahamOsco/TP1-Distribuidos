from system.commonsSystem.utils.log import initialize_config_log, get_host_name, get_service_name, ids_to_msg
from common.socket.Socket import Socket
from common.protocol.Protocol import Protocol
from system.leader.ControlValue import ControlValue 
from system.leader.ServerUDP import ServerUDP 
from system.leader.HealthCheck import HealthCheck 

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
TIME_OUT_TO_FIND_LEADER = 10
TIME_OUT_TO_GET_ACK = 7
MAX_SIZE_QUEUE_PROTO_CONNECT = 5


class LeaderElection:
    def __init__(self):
        signal.signal(signal.SIGTERM, self.sign_term_handler)
        self.config_params = initialize_config_log()
        self.joins = []
        self.id = int(os.getenv("NODE_ID"))
        self.ring_size = int(os.getenv("RING_SIZE"))
        self.queue_proto_connect = queue.Queue(maxsize =MAX_SIZE_QUEUE_PROTO_CONNECT)
        self.send_connect_control = threading.Lock()
        self.send_peer_control = threading.Lock()
        self.leader_id = ControlValue(-1)
        self.got_ack = ControlValue(-1)
        self.stop_value = ControlValue(False)
        self.reset_skts_and_protocols()

    def start_server_udp(self):
        self.server_udp = ServerUDP(self.id, get_service_name(self.id))
        thr_server_udp = threading.Thread(target=self.server_udp.run)
        thr_server_udp.start()
        self.joins.append(thr_server_udp)

    def reset_skts_and_protocols(self):
        self.server_udp = None
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
        
    def thread_accepter(self):
        self.skt_accept = Socket(port = get_service_name(self.id))
        while True:
            skt_peer, addr = self.skt_accept.accept_simple()
            if not skt_peer:
                logging.info(f"action: accept socket was closed! ✅ ")
                break
            else:
                thr_client = threading.Thread(target =self.thread_client, args=(skt_peer, ))
                thr_client.start()
                self.joins.append(thr_client)

    def getNextId(self, aId: int):
        return ((aId - 100 + 1) % self.ring_size) + 100
    

    def find_new_leader(self):
        self.release_resources()
        #self.start_server_udp()
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
                    logging.info(f"[{self.id}] Leader found!: {self.leader_id.value}")
                elif (time.time() - start_time) >= TIME_OUT_TO_FIND_LEADER:
                    logging.info(f"[{self.id}] Timeout to find a leader!")
                break
        logging.info(f"[{self.id}] Finish new Leader 🪜🗡️ Now the leader is {self.leader_id.value}")
        
    def condition_to_get_ack(self, next_id :int):
        return self.got_ack.is_this_value(next_id)

    def my_dni(self, identity: str):
        if identity == "Connect":
            return f"[{self.id}] Connect"
        elif identity == "Peer":
            return f"[{self.id}] Peer"

    def send_message_proto_connect_with_lock(self, message: str, next_id:int = -1):
        with self.send_connect_control:
            self.protocol_connect.send_string(message)
            if (next_id != -1):
                logging.info(f"{self.my_dni('Connect')} Send: {message} to: {next_id} ⌚")
            else:
                logging.info(f"{self.my_dni('Connect')} Send: {message}")

    def send_message_proto_peer_with_lock(self, message: str):
        with self.send_peer_control:
            self.protocol_peer.send_string(message)
            logging.info(f"{self.my_dni('Peer')} Send: {message}")
    
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
                logging.info(f"[{self.id}] Recv: {message_recv} 🎃")
                message_type, ids_recv = self.parse_message(message_recv)
                if (message_type == MESSG_ACK):
                    self.ack_message_handler(ids_recv[0])
                else:
                    logging.info(f"{self.my_dni('Connect')} Another messages!! {message_recv} ")
            except Exception as e :
                if self.skt_connect and self.skt_connect.is_closed():
                    break
                logging.info(f"action: We catch the error: {e} ✅")
                break
        
    def send_message_and_wait_for_ack(self, message: str, next_id: int, ):
        if self.protocol_connect is None:
            self.protocol_connect = Protocol(self.skt_connect)
            thr_receiver_connect = threading.Thread(target= self.thread_receiver_connect)
            thr_receiver_connect.start()
            self.joins.append(thr_receiver_connect)
        self.send_message_proto_connect_with_lock(message, next_id)
        start_time = time.time()
        while True:
            with self.got_ack.condition:
                result = self.got_ack.condition.wait_for(lambda: self.condition_to_get_ack(next_id), TIME_OUT_TO_GET_ACK)
                if result:
                    logging.info(f"{self.my_dni('Connect')} We got a ack! good from {next_id} ✅")
                    break
                elif (time.time() - start_time) >= TIME_OUT_TO_GET_ACK:
                    logging.info(f"{self.my_dni('Connect')} Timeout to get a ack! from {next_id} We try with the next!")
                    if self.skt_connect:
                        self.skt_connect.close()
                    self.skt_connect = None
                    self.protocol_connect = None
                    self.safe_send_next(message, next_id)        

    def safe_send_next(self, message: str, a_id: int):
        next_id = self.getNextId(a_id)
        if a_id == next_id:
            logging.info(f"action: safe_send_next | message: mssg dio toda la vuelta! | result: success  ❌")
            raise Exception("Di toda la vuelta sin ninguna respuestas!")
        self.got_ack.change_value(None)
        if self.skt_connect == None and self.protocol_connect == None:
            can_connect = False
            while not can_connect: 
                logging.info(f"[{self.id}] Trying to connect to {next_id}  🔄")
                self.skt_connect = Socket(ip= get_host_name(next_id), port= get_service_name(next_id))
                can_connect, msg = self.skt_connect.connect() #ver si borrar esto. 
                #logging.info(f"[{self.id}] Is connected the skt: {self.skt_connect.is_connected()} 🔥⛵")
                if can_connect:
                    logging.info(f"[{self.id}] We connect to {next_id}  ✅")
                    self.queue_proto_connect.put("Socket Created successfully ✅ 🌟🌟")
                    self.send_message_and_wait_for_ack(message, next_id)
                else:
                    logging.info(f"[{self.id}] We can't connect to {next_id}  ❌")
                    next_id = self.getNextId(next_id)
        elif self.skt_connect:
            self.send_message_and_wait_for_ack(message, next_id)
    

    def get_message(self):
        if self.protocol_connect is None:
            result = self.queue_proto_connect.get()
            logging.info(f"[{self.id}] message_recv from queue: {result} 🤯 ")
        message_recv = self.protocol_peer.recv_string()
        logging.info(f"[{self.id}] Recv: {message_recv} 🎃")
        return self.parse_message(message_recv)

    def thread_receiver_peer(self):
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
                else:
                    logging.info(f"action: Recv a strager message??: {message_recv} | result: success 🦸")
            except Exception as e:
                if self.skt_peer and self.skt_peer.is_closed():
                    break
                logging.info(f"action: We catch the error: {e}")
                #traceback.print_exc()  # Imprime la traza completa del error
                break
        logging.info(f"action: thread_receiver_peer, stopping control | result: success 🦸")
        self.stop_value.change_value(False)
        self.stop_value.notify_all()
    
    def stop(self):
        self.stop_value.change_value(True)
        self.stop_value.notify_all()
        self.release_resources()

    def thread_client(self, skt_peer):
        self.skt_peer = skt_peer
        self.protocol_peer = Protocol(self.skt_peer)
        thr_receiver = threading.Thread(target= self.thread_receiver_peer)
        thr_receiver.start()
        self.joins.append(thr_receiver)
    
    def release_threads(self):
        for thr in self.joins:
            if thr.is_alive():
                thr.join()
        self.joins.clear()

    def release_resources(self):
        if self.server_udp:
            self.server_udp.stop()
        if self.skt_accept:
            self.skt_accept.close()
        if self.skt_connect:
            self.skt_connect.close()
        if self.skt_peer:
            self.skt_peer.close()
        self.reset_skts_and_protocols()
        logging.info(f"Amount of threads to join: {len(self.joins)}")
        self.release_threads()
        logging.info(f"All resource are free 💯")
    
