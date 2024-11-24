from system.commonsSystem.utils.log import initialize_config_log
from system.commonsSystem.utils.connectionLeader import get_host_name, get_service_name, OFFSET_MEDIC_HOSTNAME
from common.socket.Socket import Socket
from common.protocol.Protocol import Protocol
from system.commonsSystem.DTO.TokenDTO import TokenDTO, TypeToken
from system.leader.LeaderProtocol import LeaderProtocol
from system.leader.ControlValue import ControlValue 
from system.leader.InternalMedicServer import InternalMedicServer 
from system.leader.InternalMedicCheck import InternalMedicCheck 
from system.commonsSystem.heartbeatClient.HeartbeatClient import HeartbeatClient
from system.leader.HeartbeatServer import HeartbeatServer
from system.leader.Monitor import Monitor
import threading
import os
import logging
import time
import queue
import signal
import sys

EXIT = "EXIT"
CAN_RECV_MESSAGE = "CanRecvMessage"
HAVE_NEW_SKT_PEER = "NewSocketPeer"
TIME_OUT_TO_FIND_LEADER = 15
TIME_OUT_TO_GET_ACK = 5
MAX_SIZE_QUEUE_PROTO_CONNECT = 1
TIME_FOR_BOOSTRAPING = 1.5
TIME_FOR_SLEEP_OBS_LEADER = 0.5

class LeaderElection:
    def __init__(self):
        self.config_params = initialize_config_log()
        self.joins = []
        self.heartbeat_client = None
        self.heartbeat_server = None
        self.my_numeric_ip = Socket.get_my_numeric_ip()
        self.ring_size = int(os.getenv("RING_SIZE"))
        self.id = int(os.getenv("NODE_ID"))
        self.next_id_lock = Monitor(self.getNextId(self.id))
        self.queue_proto_connect = queue.Queue(maxsize =MAX_SIZE_QUEUE_PROTO_CONNECT)
        self.send_connect_control = threading.Lock()
        self.leader_id = ControlValue(None)
        self.got_ack = ControlValue(None)
        self.reset_skts_and_protocols()
        self.thr_obs_leader = None
        self.sigterm_monitor = Monitor(False)
        self.can_observer_lider = True
        self.start_resource_unique()
        signal.signal(signal.SIGTERM, self.sign_term_handler)

    def thread_observer_leader(self):
        while self.leader_id.value and self.sigterm_monitor.is_this_value(False):
            leader_is_alive = InternalMedicCheck.is_alive_with_ip(self.id, self.leader_id.value[0], self.leader_id.value[1], verbose= -1)
            if (self.sigterm_monitor.is_this_value(False) and not leader_is_alive):
                logging.info(f"[{self.id}] Current Leader is dead! 💀")
                InternalMedicCheck.set_leader_id_dead(self.leader_id.value[0])
                self.leader_id.change_value(None)
                self.internal_medic_server.set_leader_data(None)
                self.find_new_leader()
            time.sleep(TIME_FOR_SLEEP_OBS_LEADER)

    def start_resource_unique(self):
        self.internal_medic_server = InternalMedicServer(self.id)
        self.internal_medic_server.run()
        self.heartbeat_client = HeartbeatClient(self.id)
        self.heartbeat_client.run()

    def wait_boostrap_leader(self):
        self.next_id_lock.set_value(self.getNextId(self.id)) #el Next_id sera el id actual.
        self.start_accept()
        time.sleep(TIME_FOR_BOOSTRAPING)
        self.leader_id.change_value(None)

    def there_is_leader_already(self) -> bool:
        leader_data = InternalMedicCheck.try_get_leader_data(self.id, self.getNextId(self.id))
        if leader_data != None:
            self.leader_id.change_value(leader_data)
            self.internal_medic_server.set_leader_data(leader_data)
            self.start_observer_leader()
            return True
        return False

    def wait_to_get_leader(self):
        start_time = time.time()
        while self.sigterm_monitor.is_this_value(False):
            with self.leader_id.condition:
                result_leader = self.leader_id.condition.wait_for(
                    lambda: not self.leader_id.is_this_value(None), TIME_OUT_TO_FIND_LEADER)
                if self.sigterm_monitor.is_this_value(True):
                    return
                if result_leader:
                    break
                elif (time.time() - start_time) >= TIME_OUT_TO_FIND_LEADER: 
                    logging.info(f"[{self.id}] Timeout to find a leader!")
                    return
                break
        self.internal_medic_server.set_leader_data(self.leader_id.value)
        if self.leader_id.value and self.leader_id.value[0] == self.id and self.heartbeat_server is None:
            logging.info(f"[{self.id}] I'm the leader medic! ⛑️")
            self.heartbeat_server = HeartbeatServer(get_host_name(self.id), get_service_name(self.id))
            self.heartbeat_server.run()
            InternalMedicCheck.clean_leader_id()
        if self.leader_id.value:
            logging.info(f"[{self.id}] Finish We have a new Lider {self.leader_id.value[0]} ⛑️ ")

    def start_observer_leader(self):
        self.thr_obs_leader = threading.Thread(target=self.thread_observer_leader)
        self.thr_obs_leader.start()

    def find_new_leader(self):
        if self.sigterm_monitor.is_this_value(True):
            return 
        self.free_resources()
        self.wait_boostrap_leader()
        if self.sigterm_monitor.is_this_value(False) and self.there_is_leader_already(): 
            return
        logging.info(f" 👉Starting search a new leader! 👈 ✅")
        token_dto = TokenDTO(a_type= TypeToken.ELECTION, dic_medics= {self.id: self.my_numeric_ip})
        self.safe_send_next(token_dto)
        try: 
            self.wait_to_get_leader()
            if self.thr_obs_leader is None and self.leader_id.value and self.leader_id.value[0] != self.id:
                self.start_observer_leader()
        except TypeError as e:
            logging.info(f"Catcheando Excepcion of type (index) ✅")
            return

    def reset_socket_connection(self, token_dto: TokenDTO):
        logging.info(f"[{self.id}] This Node {get_host_name(self.next_id_lock.get_value())} is dead, Let's skt connect to None ")
        if self.skt_connect:
            self.skt_connect.close()
        self.skt_connect = None
        self.protocol_connect = None
        self.next_id_lock.set_value(value=self.getNextId(self.next_id_lock.get_value()))


    def send_message_and_wait_for_ack(self, token_dto: TokenDTO):
        current_next_id = self.next_id_lock.get_value()
        self.send_message_proto_connect_with_lock(token_dto)
        start_time = time.time()
        with self.got_ack.condition:
            result = self.got_ack.condition.wait_for(lambda: self.is_got_ack_this_value(current_next_id), TIME_OUT_TO_GET_ACK)
            if result:
                return
            elif (time.time() - start_time) >= TIME_OUT_TO_GET_ACK:
                next_id_to_compare = self.next_id_lock.get_value()
                logging.info(f"[{self.id}] Connect Timeout to get a ack! from {current_next_id} Type: {token_dto.a_type.value} {token_dto.dic_medics}  We try with the next! 🔕 {next_id_to_compare} 👈")
                if not self.leader_id.is_this_value(None):
                    logging.info(f"[{self.id}] We found a leader already! Leader:{self.leader_id.value} 💯 ✅")
                    return
                if not InternalMedicCheck.is_alive(self.id, self.next_id_lock.get_value()):
                    self.reset_socket_connection(token_dto)
                self.safe_send_next(token_dto)

    def create_connect_and_send_message(self, token_dto: TokenDTO):
        self.skt_connect = Socket(ip= get_host_name(self.next_id_lock.get_value()), port= get_service_name(self.next_id_lock.get_value()))
        can_connect, _ = self.skt_connect.connect()
        if can_connect:
            self.protocol_connect = LeaderProtocol(self.skt_connect)
            self.queue_proto_connect.put(CAN_RECV_MESSAGE)
            thr_receiver_connect = threading.Thread(target= self.thread_receiver_connect)
            thr_receiver_connect.start()
            self.joins.append(thr_receiver_connect)
            self.send_message_and_wait_for_ack(token_dto)

    def safe_send_next(self, token_dto: TokenDTO):
        if self.next_id_lock.is_this_value(self.id):
            raise Exception("I went all around without any answers ❌")
        self.got_ack.change_value(None)
        try:
            if self.skt_connect and self.protocol_connect:
                self.send_message_and_wait_for_ack(token_dto)
            else:
                while self.sigterm_monitor.is_this_value(False):
                    logging.info(f"[{self.id}] Trying to connect to {self.next_id_lock.get_value()} 🔄")
                    if InternalMedicCheck.is_alive(self.id, self.next_id_lock.get_value()):
                        self.create_connect_and_send_message(token_dto)
                        return True
                    else:
                        logging.info(f"[{self.id}] We can't connect to {self.next_id_lock.get_value()}  ❌")
                        self.next_id_lock.set_value(value=self.getNextId(self.next_id_lock.get_value()))
        except OSError as e:
            logging.info(f"Catcheando Excepcion {e} ✅")
            return

    def send_message_proto_connect_with_lock(self, token_dto: TokenDTO):
        try:
            with self.send_connect_control:
                self.protocol_connect.send_tokenDTO(token_dto)
        except OSError as e:
            return

    def send_message_ack_proto_peer(self):
        token_dto = TokenDTO(a_type= TypeToken.ACK, dic_medics={self.id: self.my_numeric_ip})
        try:
            self.protocol_peer.send_tokenDTO(token_dto)
        except OSError as e:
            return        

    def election_message_handler(self, token_dto: TokenDTO):
        if self.id in token_dto.dic_medics:
            leader_id = max(token_dto.dic_medics.keys())
            token_dto.leader_id = leader_id
            token_dto.numeric_ip_leader = token_dto.dic_medics[leader_id]
            token_dto.a_type = TypeToken.COORDINATOR
            token_dto.dic_medics = {self.id: self.my_numeric_ip}
            self.send_message_proto_connect_with_lock(token_dto)
        else:
            token_dto.dic_medics[self.id] = self.my_numeric_ip
            thr_continue_election = threading.Thread(target= self.safe_send_next, args=(token_dto, ))
            thr_continue_election.start()
            self.joins.append(thr_continue_election)
        self.send_message_ack_proto_peer()

    def coordinator_message_handler(self, token_dto: TokenDTO):
        self.leader_id.change_value((token_dto.leader_id, token_dto.numeric_ip_leader))
        self.leader_id.notify_all()
        if self.id not in token_dto.dic_medics:
            token_dto.dic_medics[self.id] = self.my_numeric_ip
            thr_continue_coord = threading.Thread(target= self.safe_send_next, args=(token_dto, ))
            thr_continue_coord.start()
            self.joins.append(thr_continue_coord)
        self.send_message_ack_proto_peer()
        
    def thread_receiver_peer(self):
        result = self.queue_proto_connect.get()
        if result == EXIT:
            return
        while self.sigterm_monitor.is_this_value(False):
            try: 
                token_dto = self.protocol_peer.recv_tokenDTO()
                if (token_dto.a_type == TypeToken.ACK):
                    self.ack_message_handler(token_dto)
                elif (token_dto.a_type == TypeToken.ELECTION):
                    self.election_message_handler(token_dto)
                elif (token_dto.a_type == TypeToken.COORDINATOR):
                    self.coordinator_message_handler(token_dto)
            except Exception as e:
                logging.info(f"Error {e} 👈 in ThrRecv Peer ✅")
                if self.sigterm_monitor.is_this_value(False):
                    self.protocol_peer = None
                    if self.skt_peer:
                        self.skt_peer.close()
                    self.queue_proto_connect.put(HAVE_NEW_SKT_PEER)
                    logging.info(f"[{self.id}] Current skt Peer is broken 👈 we will have a new! ✅ ")
                    break
                if self.skt_peer and self.skt_peer.is_closed():
                    break
                return

    def thread_receiver_connect(self):
        while self.sigterm_monitor.is_this_value(False):
            try:
                token_dto = self.protocol_connect.recv_tokenDTO()
                if (token_dto.a_type == TypeToken.ACK):
                    self.ack_message_handler(token_dto)
            except Exception as e :
                return

    def thread_accepter(self):
        self.skt_accept = Socket(port = get_service_name(self.id))
        while self.sigterm_monitor.is_this_value(False):
            skt_peer, addr = self.skt_accept.accept_simple()
            if not skt_peer:
                return
            else:
                logging.info(f"There's a new socket peer! 🤝 ✅ {skt_peer.get_addr_from_connect()}")
                self.skt_peer = skt_peer
                self.protocol_peer = LeaderProtocol(self.skt_peer)
                thr_receiver = threading.Thread(target= self.thread_receiver_peer)
                thr_receiver.start()
                self.joins.append(thr_receiver)

    def getNextId(self, aId: int):
        return ((aId - OFFSET_MEDIC_HOSTNAME + 1) % self.ring_size) + OFFSET_MEDIC_HOSTNAME

    def is_got_ack_this_value(self, next_id :int):
        return self.got_ack.is_this_value(next_id)

    def ack_message_handler(self, token_dto:TokenDTO):
        self.got_ack.change_value(list(token_dto.dic_medics.keys())[0])
        self.got_ack.notify_all()

    def start_accept(self):
        thr_accepter = threading.Thread(target=self.thread_accepter)
        thr_accepter.start()
        self.joins.append(thr_accepter)

    def reset_skts_and_protocols(self):
        self.skt_peer = None
        self.skt_connect = None
        self.protocol_connect = None
        self.protocol_peer = None
        self.skt_accept = None

    def sign_term_handler(self, signum, frame):
        self.sigterm_monitor.set_value(True)
        logging.info(f"action: ⚡ Signal Handler | signal: {signum} | result: success ✅")
        if self.queue_proto_connect.empty():
            self.queue_proto_connect.put(EXIT)
        self.free_resources()
        if self.thr_obs_leader:
            self.can_observer_lider = False
            self.thr_obs_leader.join()
        if self.heartbeat_client:
            self.heartbeat_client.free_resources()
        if self.internal_medic_server:
            self.internal_medic_server.free_resources()
        if self.heartbeat_server:
            self.heartbeat_server.free_resources()
            self.heartbeat_server = None
        logging.info(f"[Leader Election] All resource are free 💯")

    def release_threads(self):
        for thr in self.joins:
            thr.join()
        self.joins.clear()

    def free_resources(self):
        if self.skt_accept and not self.skt_accept.is_closed():
            self.skt_accept.close()
        if self.skt_connect and not self.skt_connect.is_closed():
            self.skt_connect.close()
        if self.skt_peer and not self.skt_peer.is_closed():
            self.skt_peer.close()
        
        self.reset_skts_and_protocols()
        self.release_threads()
        if not self.queue_proto_connect.empty():
            self.queue_proto_connect.get()

