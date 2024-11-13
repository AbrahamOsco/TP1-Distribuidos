from system.commonsSystem.utils.log import initialize_config_log 
from common.socket.Socket import Socket
from common.protocol.Protocol import Protocol
import traceback
import threading
import os
import logging
import time

def get_service_name(id: int):
    return int(f"20{id}")

def get_host_name(id: int):
    return f"node{id-100}"

def ids_to_msg(message: str, ids: list[int]):
    return message + "|" + "|".join([str(x) for x in ids])

TIME_OUT_TO_FIND_LEADER = 10
TIME_OUT_TO_GET_ACK = 7

class LeaderElection:
    def __init__(self):
        self.joins = []
        self.id = int(os.getenv("NODE_ID"))
        self.ring_size = int(os.getenv("RING_SIZE"))
        self.leader_id_value = -1
        self.leader_id_control = [threading.Lock(), threading.Condition()] #0: lock, 1:condvar
        self.got_ack_value = -1
        self.got_ack_control = [threading.Lock(), threading.Condition()] #0:lock, #1: condvar
        self.stop_value = False
        self.stop_control = [threading.Lock(), threading.Condition()] #0:lock, #1: condvar
        self.config_params = initialize_config_log()
        self.hostname = get_host_name(self.id)
        self.service_name = get_service_name(self.id)
        self.next_id = self.getNextId(self.id) 
        self.skt_accept = Socket(port = self.service_name) # ej: puerto 20100 para el nodo 100
        self.skt_peer = None #socket Anterior
        self.skt_connect = None # socket sgt
        self.protocol_connect = None
        self.protocol_peer = None
        
    def am_i_leader(self):
        return self.id == self.leader_id_value
    
    def thread_accepter(self):
        while True:
            skt_peer, addr = self.skt_accept.accept_simple()
            if not skt_peer:
                logging.error(f"action: accept | result: fail ❌ | ")
            else:
                thr_client = threading.Thread(target =self.thread_client, args=(skt_peer, ))
                thr_client.start()
                self.joins.append(thr_client)
    
    def getNextId(self, aId: int):
        return ((aId - 100 + 1) % self.ring_size) + 100

    def show_my_info(self):
        logging.info(f"Id: {self.id} | NextId: {self.next_id} |" +
                     f"HostName: {self.hostname} | ServiceName: {self.service_name}")
    
    def condition_to_find_leader(self):
        self.leader_id_value is not None

    def find_new_leader(self):
        with self.stop_control[0]:
            if self.stop_value: #SI stop es true corto. 
                return
        logging.info("Searching a leader!")
        with self.leader_id_control[0]:
            self.leader_id_value = None
        # mando eleccion y espero algun ok.
        message = ids_to_msg("ELECTION", [self.id])
        start_time = time.time()
        self.safe_send_next(message, self.id)
        while True:
            with self.leader_id_control[1]:
                result_leader = self.leader_id_control[1].wait_for(self.condition_to_find_leader, TIME_OUT_TO_FIND_LEADER)
                if result_leader:
                    logging(f"[{self.id}] Leader found!: {self.leader_id_value}")
                elif (time.time() - start_time) >= TIME_OUT_TO_FIND_LEADER:
                    logging.info(f"[{self.id}] Timeout to find a leader!")
                    break
                logging.info(f"[{self.id}] waiting for find a leader still dont have a timeout {self.leader_id_value}")

    def condition_to_get_ack(self, next_id :int):
        return self.got_ack_value is not None and self.got_ack_value == next_id

    def create_protocol_connect_and_send_message(self, message: str, next_id: int, ):
        if self.protocol_connect is None:
            self.protocol_connect = Protocol(self.skt_connect)
            logging.info(f"[{self.id}] Assignd to Protocol Connect 😮 {self.protocol_connect}")
        self.protocol_connect.send_string(message)
        logging.info(f"[{self.id}] Sending: -{message}- to: {next_id}")
        start_time = time.time()
        while True:
            with self.got_ack_control[1]:
                result = self.got_ack_control[1].wait_for(lambda: self.condition_to_get_ack(next_id), TIME_OUT_TO_GET_ACK)
                if result:
                    logging.info(f"[{self.id}] We got a ack! good from {next_id} ✅")
                    break
                elif (time.time() - start_time) >= TIME_OUT_TO_GET_ACK:
                    logging.info(f"[{self.id}] Timeout to get a ack! from {next_id} We try with the next!")
                    if self.skt_connect:
                        self.skt_connect.close()
                    self.skt_connect = None
                    self.protocol_connect = None
                    self.safe_send_next(message, next_id)        


    def safe_send_next(self, message: str, a_id: int):
        next_id = self.getNextId(a_id)
        if a_id == self.next_id:
            logging.info("action: safe_send_next | message: mssg dio toda la vuelta! | result: success  ❌")
            raise Exception("Di toda la vuelta sin ninguna respuestas!")
        with self.got_ack_control[0]:
            self.got_ack_value = None # Seteo el ackfromm en None, recien arranco.
        if self.skt_connect == None and self.protocol_connect == None:
            self.skt_connect = Socket(ip= get_host_name(next_id), port= get_service_name(next_id))
            can_connect, msg = self.skt_connect.connect()
            logging.info(f"[{self.id}] Trying to connect with {next_id} 🦅 result: {can_connect}")
            if can_connect:
                logging.info(f"[{self.id}] Sender {message} to {next_id} from Send 💯")
                self.create_protocol_connect_and_send_message(message, next_id)
            else:
                logging.info(f"Error No pude conectarme que paso aca? 🤯 ❌ 🪓 {self.skt_connect} {self.protocol_connect}")
        elif self.skt_connect:
            logging.info(f"[{self.id}] Sender {message} to {next_id} from RECV 🥈")
            self.create_protocol_connect_and_send_message(message, next_id)

    def run(self):
        thr_accepter = threading.Thread(target=self.thread_accepter)
        thr_accepter.start()
        self.joins.append(thr_accepter)
        self.find_new_leader()
        # Aca ahora se bloquean tratandod de hacer join, pero luego tieen q haber businnes logic aca  
        self.release_threads()
        logging.info(f"End Run 🔚 🍨")
        
      # Peer solo recibe mensajes, del nodo anterior Ej peer de un nodo 2, recibe mensajes del nodo 1.
    # Parsea el mensaje del estilo "ELECTION|3|100|101|102" y retorna el tipo de mensaje y los ids de los 
    def parse_message(self, message: str):
        fields = message.split("|") # [ELECTION, 100, 101, 102]
        return (fields[0], [int(x) for x in fields[1:]])

    def thread_receiver_peer(self):
        try:
            while True:
                with self.stop_control[0]:
                    if self.stop_value:
                        break
                message_recv = self.protocol_peer.recv_string()
                logging.info(f"[{self.id}] Recv RAW: {message_recv} 🎃 ")
                message_type, ids_recv = self.parse_message(message_recv)
                logging.info(f"[{self.id}] Recv OK: {message_type} {ids_recv} 👈")
                if (message_type == "ACK"):
                    with self.lock_got_ack:
                        self.got_ack_value = ids_recv[0]
                        with self.got_ack_control[1]:
                            self.got_ack_control[1].notify_all()
                elif (message_type == "ELECTION"):
                    message_to_send = ids_to_msg("ACK", [self.id])
                    self.protocol_peer.send_string(message_to_send)
                    if self.id in ids_recv:
                        leader_id = max(ids_recv)
                        message_to_send = ids_to_msg("COORDINATOR", [leader_id, self.id])
                        self.protocol_peer.send_string(message_to_send)
                    else:
                        logging.info(f"self.id in ids_recv {self.id in ids_recv}")
                        ids_recv.append(self.id)
                        message_to_send = ids_to_msg("ELECTION", ids_recv)
                        thr_continue_election = threading.Thread(target= self.safe_send_next, args=(message_to_send, self.id,))
                        thr_continue_election.start()
                        self.joins.append(thr_continue_election)
                elif (message_type == "COORDINATOR"):
                    message_to_send = ids_to_msg("ACK", [self.id])
                    self.protocol_peer.send_string(message_to_send)
                    with self.leader_id_control[1]: 
                        self.leader_id_control[1].notify_all()
                    with self.lock_leader_id:
                        self.leader_id_value = ids_recv[0]
                    if self.id not in ids_recv:
                        ids_recv.push(self.id)
                        message_to_send = ids_to_msg("COORDINATOR", ids_recv)
                        thr_continue_coord = threading.Thread(target= self.safe_send_next, args=(message_to_send, self.id, ))
                        thr_continue_coord.start()
                        self.joins.append(thr_continue_coord)
                else:
                    logging.info(f"action: Recv a strager message??: {message_recv} | result: success 🦸")
        except Exception as e:
            logging.error(f"action: recv_string from Peer | result: fail ❌ | error: {e}")
            traceback.print_exc()  # Imprime la traza completa del error
        with self.stop_control[0]:
            self.stop_value = False
        
        with self.stop_control[1]:
            self.stop_control[1].notify_all()

    # Aca el skt connect (q envia al sgt ej nodo1 al nodo 2)
    def thread_sender(self):
        i = 0
        while True:
            try:
                logging.info(f"Sleeping for 5 sec Nº: {i}")
                time.sleep(5)
            except Exception as e:
                logging.error(f"action: send message | result: fail ❌ | error: {e}")
            i += 1

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
        self.release_threads()
    
