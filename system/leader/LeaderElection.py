from system.commonsSystem.utils.log import initialize_config_log 
from common.socket.Socket import Socket
from common.protocol.Protocol import Protocol
import traceback
import threading
import os
import logging
import time
import queue
import signal

def get_service_name(id: int):
    return int(f"20{id}")

def get_host_name(id: int):
    return f"node{id-100}"

def ids_to_msg(message: str, ids: list[int]):
    return message + "|" + "|".join([str(x) for x in ids])

MESSG_COORD = "COORDINATOR"
MESSG_ACK = "ACK"
MESSG_ELEC = "ELECTION"
TIME_OUT_TO_FIND_LEADER = 10
TIME_OUT_TO_GET_ACK = 7
MAX_SIZE_QUEUE_PROTO_CONNECT = 5

class LeaderElection:
    def __init__(self):
        self.joins = []
        signal.signal(signal.SIGTERM, self.sign_term_handler)
        self.id = int(os.getenv("NODE_ID"))
        self.ring_size = int(os.getenv("RING_SIZE"))
        self.leader_id_value = -1
        self.queue_proto_connect = queue.Queue(maxsize =MAX_SIZE_QUEUE_PROTO_CONNECT)
        self.send_connect_control = threading.Lock()
        self.send_peer_control = threading.Lock()
        self.leader_id_control = [threading.Lock(), threading.Condition()] #0: lock, 1:condvar
        self.got_ack_value = -1
        self.got_ack_control = [threading.Lock(), threading.Condition()] #0:lock, #1: condvar
        self.stop_control = [threading.Lock(), threading.Condition()] #0:lock, #1: condvar
        self.stop_value = False
        self.config_params = initialize_config_log()
        self.next_id = self.getNextId(self.id) 
        self.skt_accept = Socket(port = get_service_name(self.id)) # ej: puerto 20100 para el nodo 100
        self.skt_peer = None #socket Anterior
        self.skt_connect = None # socket sgt
        self.protocol_connect = None
        self.protocol_peer = None

    def sign_term_handler(self, signum, frame):
        logging.info(f"action: ⚡ Signal Handler | signal: {signum} | result: success ✅")
        self.release_resources()

    def am_i_leader(self):
        return self.id == self.leader_id_value
    
    def thread_accepter(self):
        while True:
            skt_peer, addr = self.skt_accept.accept_simple()
            if not skt_peer:
                logging.error(f"action:Socket accept was closed! ✅ ")
                break
            else:
                thr_client = threading.Thread(target =self.thread_client, args=(skt_peer, ))
                thr_client.start()
                self.joins.append(thr_client)

    def getNextId(self, aId: int):
        return ((aId - 100 + 1) % self.ring_size) + 100
    
    def condition_to_find_leader(self):
        with self.leader_id_control[0]:
            return self.leader_id_value is not None

    def find_new_leader(self):
        with self.stop_control[0]:
            if self.stop_value: #SI stop es true corto. 
                return
        logging.info(f"[{self.id}] Searching a leader!")
        with self.leader_id_control[0]:
            self.leader_id_value = None

        message = ids_to_msg(MESSG_ELEC, [self.id])
        start_time = time.time()
        self.safe_send_next(message, self.id)
        while True:
            with self.leader_id_control[1]:
                result_leader = self.leader_id_control[1].wait_for(self.condition_to_find_leader, TIME_OUT_TO_FIND_LEADER)
                if result_leader:
                    logging.info(f"[{self.id}] Leader found!: {self.leader_id_value}")
                    break
                elif (time.time() - start_time) >= TIME_OUT_TO_FIND_LEADER:
                    logging.info(f"[{self.id}] Timeout to find a leader!")
                    break
                logging.info(f"[{self.id}] waiting for find a leader still dont have a timeout {self.leader_id_value}")

    def condition_to_get_ack(self, next_id :int):
        return self.got_ack_value is not None and self.got_ack_value == next_id

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
        with self.got_ack_control[0]:
            self.got_ack_value = ack_value
            with self.got_ack_control[1]:
                self.got_ack_control[1].notify_all()

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
                if self.skt_connect.is_closed():
                    break
                logging.error(f"action: There a error: {e}")
                break
        
    def create_protocol_connect_and_send_message(self, message: str, next_id: int, ):
        if self.protocol_connect is None:
            self.protocol_connect = Protocol(self.skt_connect)
            self.queue_proto_connect.put("Protocol Connect was created!")
            thr_receiver_connect = threading.Thread(target= self.thread_receiver_connect)
            thr_receiver_connect.start()
            self.joins.append(thr_receiver_connect)
        self.send_message_proto_connect_with_lock(message, next_id)
        start_time = time.time()
        while True:
            with self.got_ack_control[1]:
                result = self.got_ack_control[1].wait_for(lambda: self.condition_to_get_ack(next_id), TIME_OUT_TO_GET_ACK)
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
        if a_id == self.next_id:
            logging.info(f"action: safe_send_next | message: mssg dio toda la vuelta! | result: success  ❌")
            raise Exception("Di toda la vuelta sin ninguna respuestas!")
        with self.got_ack_control[0]:
            self.got_ack_value = None # Seteo el ackfromm en None, recien arranco.
        
        if self.skt_connect == None and self.protocol_connect == None:
            self.skt_connect = Socket(ip= get_host_name(next_id), port= get_service_name(next_id))
            can_connect, msg = self.skt_connect.connect()
            if can_connect:
                self.create_protocol_connect_and_send_message(message, next_id)
            else:
                logging.info(f"Error No pude conectarme que paso aca? 🤯 ❌ 🪓 {self.skt_connect} {self.protocol_connect}")
        elif self.skt_connect:
            self.create_protocol_connect_and_send_message(message, next_id)

    def run(self):
        thr_accepter = threading.Thread(target=self.thread_accepter)
        thr_accepter.start()
        self.joins.append(thr_accepter)
        self.find_new_leader()
        logging.info(f"[{self.id}] Finish new Leader 🪜🗡️ Now the leader is {self.leader_id_value}")
        self.release_threads()
        logging.info(f"End Run 🔚 🍨")
        
    def parse_message(self, message: str):
        fields = message.split("|") # [ELECTION, 100, 101, 102]
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
        with self.leader_id_control[0]:
            self.leader_id_value = ids_recv[0]
        with self.leader_id_control[1]: 
            self.leader_id_control[1].notify_all()
        if self.id not in ids_recv:
            ids_recv.append(self.id)
            message_to_send = ids_to_msg(MESSG_COORD, ids_recv)
            thr_continue_coord = threading.Thread(target= self.safe_send_next, args=(message_to_send, self.id, ))
            thr_continue_coord.start()
            self.joins.append(thr_continue_coord)
        message_to_send = ids_to_msg(MESSG_ACK, [self.id])
        self.send_message_proto_peer_with_lock(message_to_send)

    def get_message(self):
        if self.protocol_connect is None:
            result = self.queue_proto_connect.get()
        message_recv = self.protocol_peer.recv_string()
        logging.info(f"[{self.id}] Recv: {message_recv} 🎃")
        return self.parse_message(message_recv)


    def thread_receiver_peer(self):
        while True:
            try: 
                with self.stop_control[0]:
                    if self.stop_value:
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
                if self.skt_peer.is_closed():
                    break
                logging.error(f"action: There a error: {e}")
                #traceback.print_exc()  # Imprime la traza completa del error
                break
        
        logging.info(f"action: thread_receiver_peer, stopping control | result: success 🦸")
        with self.stop_control[0]:
            self.stop_value = False
        with self.stop_control[1]:
            self.stop_control[1].notify_all()

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
                
    def release_resources(self):
        if self.skt_accept:
            self.skt_accept.close()
        if self.skt_connect:
            self.skt_connect.close()
        if self.skt_peer:
            self.skt_peer.close()
        logging.info(f"Amount of threads to join: {len(self.joins)}")
        self.release_threads()
        logging.info(f"All resource are free 💯")
    
