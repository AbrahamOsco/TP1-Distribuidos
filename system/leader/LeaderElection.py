from system.commonsSystem.utils.log import initialize_config_log
from system.commonsSystem.utils.connectionLeader import get_host_name, get_service_name, OFFSET_MEDIC_HOSTNAME
from system.leader.common_leader import ids_to_msg
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
TIME_OUT_TO_FIND_LEADER = 16
TIME_OUT_TO_GET_ACK = 15
MAX_SIZE_QUEUE_PROTO_CONNECT = 1
TIME_FOR_BOOSTRAPING = 1.0
TIME_FOR_SLEEP_OBS_LEADER = 0.5

class LeaderElection:
    def __init__(self):
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
        self.reset_skts_and_protocols()
        self.resource_control = threading.Lock()
        self.thr_obs_leader = None
        self.skt_accept = None
        self.skt_peer = None
        self.can_observer_lider = True
        self.start_resource_unique()
        signal.signal(signal.SIGTERM, self.sign_term_handler)

    # Una vez que exista un primer lider se inicia el observer. 
    def thread_observer_leader(self):
        logging.info(f"[{self.id}] Starting to observer to the leader (if there is any)! 👀 ")
        while self.can_observer_lider:
            leader_is_alive = InternalMedicCheck.is_alive(self.id, self.leader_id.value, verbose =0)
            if (not leader_is_alive): # Si murio el lider actual seteamos None y search a new lider.
                logging.info(f"[{self.id}] Currnet Leader is dead! 💀, Searching a new leader 🔄")
                self.leader_id.change_value(None)
                self.internal_medic_server.set_leader_id(None)
                self.find_new_leader()
            time.sleep(TIME_FOR_SLEEP_OBS_LEADER)

    def start_resource_unique(self):
        self.internal_medic_server = InternalMedicServer(self.id)
        self.internal_medic_server.run()
        self.heartbeat_client = HeartbeatClient(get_host_name(self.id), get_service_name(self.id))
        self.heartbeat_client.run()

    def wait_boostrap_leader(self):
        self.start_accept()
        logging.info(f"[{self.id}] Bootstrapping search of a new lider {TIME_FOR_BOOSTRAPING}s 🎖️ ⏳⏳")
        time.sleep(TIME_FOR_BOOSTRAPING) # Wait to the other nodes to be ready
        self.leader_id.change_value(None)

    def there_is_leader_already(self) -> bool:
        leader_id = InternalMedicCheck.try_to_get_leader_id(self.id, self.getNextId(self.id))
        if leader_id != None:
            logging.info(f"There is a leader already! 🎖️ {leader_id}")
            self.leader_id.change_value(leader_id)
            self.internal_medic_server.set_leader_id(leader_id)
            self.start_observer_leader()
            return True
        #logging.info("There is not 🙅 a leader in the ring 🛟👌")
        return False

    def wait_to_get_leader(self):
        start_time = time.time()
        while True:
            with self.leader_id.condition:
                result_leader = self.leader_id.condition.wait_for(
                    lambda: not self.leader_id.is_this_value(None), TIME_OUT_TO_FIND_LEADER)
                if result_leader:
                    break
                elif (time.time() - start_time) >= TIME_OUT_TO_FIND_LEADER: 
                    logging.info(f"[{self.id}] Timeout to find a leader!")
                break
        self.internal_medic_server.set_leader_id(self.leader_id.value)
        if self.leader_id.is_this_value(self.id) and self.heartbeat_server is None:
            logging.info(f"[{self.id}] I'm the leader medic! ⛑️")
            self.heartbeat_server = HeartbeatServer(get_host_name(self.id), get_service_name(self.id))
            self.heartbeat_server.run()
        logging.info(f"[{self.id}] Finish new Leader 🪜🗡️ Now the leader is {self.leader_id.value}")
    
    def start_observer_leader(self):
        self.thr_obs_leader = threading.Thread(target=self.thread_observer_leader)
        self.thr_obs_leader.start()

    def find_new_leader(self):
        self.free_resources()
        self.wait_boostrap_leader()
        if self.there_is_leader_already(): 
            return
        message = ids_to_msg(MESSG_ELEC, [self.id])
        self.safe_send_next(message, self.id)
        self.wait_to_get_leader()
        if self.thr_obs_leader is None and not self.leader_id.is_this_value(self.id):
            self.start_observer_leader()


    def send_message_and_wait_for_ack(self, message: str, next_id: int, ):
        self.send_message_proto_connect_with_lock(message, next_id)
        start_time = time.time()
        while True:
            with self.got_ack.condition:
                result = self.got_ack.condition.wait_for(lambda: self.is_got_ack_this_value(next_id), TIME_OUT_TO_GET_ACK)
                if result:
                    break
                elif (time.time() - start_time) >= TIME_OUT_TO_GET_ACK:
                    logging.info(f"[{self.id}] Connect Timeout to get a ack! from {next_id} We try with the next! 🔕")
                    if not self.leader_id.is_this_value(None):
                        logging.info(f"[{self.id}] We found a leader already! Leader:{self.leader_id.value} 💯 ✅")
                        break
                    with self.resource_control:
                        if self.skt_connect and not self.skt_connect.is_closed():
                            self.skt_connect.close()
                    self.skt_connect = None
                    self.protocol_connect = None
                    self.safe_send_next(message, next_id)

    def create_connect_and_send_message(self, next_id: int, message: str):
        self.skt_connect = Socket(ip= get_host_name(next_id), port= get_service_name(next_id))
        can_connect, _ = self.skt_connect.connect()
        if can_connect:
            self.protocol_connect = Protocol(self.skt_connect)
            self.queue_proto_connect.put("Protoconnect Created! ✅")
            thr_receiver_connect = threading.Thread(target= self.thread_receiver_connect)
            thr_receiver_connect.start()
            self.joins.append(thr_receiver_connect)
            self.send_message_and_wait_for_ack(message, next_id)

    def safe_send_next(self, message: str, a_id: int):
        next_id = self.getNextId(a_id)
        if a_id == next_id:
            raise Exception("I went all around without any answers ❌")
        self.got_ack.change_value(None)
        if self.skt_connect and self.protocol_connect:
            self.send_message_and_wait_for_ack(message, next_id)
        else:
            while True:
                logging.info(f"[{self.id}] Trying to connect to {next_id} 🔄")
                if InternalMedicCheck.is_alive(self.id, next_id):
                    self.create_connect_and_send_message(next_id, message)
                    break
                else:
                    logging.info(f"[{self.id}] We can't connect to {next_id}  ❌")
                    next_id = self.getNextId(next_id)

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
            thr_continue_coord = threading.Thread(target= self.safe_send_next, args=(message_to_send, self.id,))
            thr_continue_coord.start()
            self.joins.append(thr_continue_coord)
        message_to_send = ids_to_msg(MESSG_ACK, [self.id])
        self.send_message_proto_peer_with_lock(message_to_send)

    def get_message(self):
        message_recv = self.protocol_peer.recv_string()
        logging.info(f"[{self.id}-Peer] Recv: {message_recv} 🎃")
        return self.parse_message(message_recv)

    def thread_receiver_peer(self):
        result = self.queue_proto_connect.get()
        while True:
            try: 
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
                #traceback.print_exc()
                break

    def thread_receiver_connect(self):
        while True:
            try:
                message_recv = self.protocol_connect.recv_string()
                logging.info(f"[{self.id}-Connect] Recv: {message_recv} 🎃")
                message_type, ids_recv = self.parse_message(message_recv)
                if (message_type == MESSG_ACK):
                    self.ack_message_handler(ids_recv[0])
            except Exception as e :
                break

    def thread_accepter(self):
        self.skt_accept = Socket(port = get_service_name(self.id))
        while True:
            skt_peer, addr = self.skt_accept.accept_simple()
            if not skt_peer:
                break
            else:
                self.skt_peer = skt_peer
                self.protocol_peer = Protocol(self.skt_peer)
                thr_receiver = threading.Thread(target= self.thread_receiver_peer)
                thr_receiver.start()
                self.joins.append(thr_receiver)

    def thread_client(self, skt_peer):
        self.skt_peer = skt_peer
        self.protocol_peer = Protocol(self.skt_peer)
        thr_receiver = threading.Thread(target= self.thread_receiver_peer)
        thr_receiver.start()
        self.joins.append(thr_receiver)

    def getNextId(self, aId: int):
        return ((aId - OFFSET_MEDIC_HOSTNAME + 1) % self.ring_size) + OFFSET_MEDIC_HOSTNAME

    def send_message_proto_peer_with_lock(self, message: str):
        with self.send_peer_control:
            self.protocol_peer.send_string(message)
            logging.info(f"[{self.id}-Peer]  Send: {message}")

    def is_got_ack_this_value(self, next_id :int):
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

    def reset_skts_and_protocols(self):
        self.skt_peer = None
        self.skt_connect = None
        self.protocol_connect = None
        self.protocol_peer = None

    def sign_term_handler(self, signum, frame):
        logging.info(f"action: ⚡ Signal Handler | signal: {signum} | result: success ✅")
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
        self.free_resources()

    def am_i_leader(self):
        return self.leader_id.is_this_value(self.id)

    def get_leader_id(self):
        return self.leader_id.value
    
    def release_threads(self):
        for thr in self.joins:
            if thr.is_alive():
                thr.join()
        self.joins.clear()

    def free_resources(self):
        with self.resource_control:
            if self.skt_connect and not self.skt_connect.is_closed():
                self.skt_connect.close()
        if self.skt_accept:
            self.skt_accept.close()
        if self.skt_peer:
            self.skt_peer.close()
        self.reset_skts_and_protocols()
        self.release_threads()
        logging.info(f"[LeaderElection] All resource are free 💯")

