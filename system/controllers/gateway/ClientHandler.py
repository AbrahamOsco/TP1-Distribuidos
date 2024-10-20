import logging
import signal
import os
from common.socket.Socket import Socket
from system.commonsSystem.protocol.ServerProtocol import ServerProtocol
from system.commonsSystem.broker.Broker import Broker

class ClientHandler:
    def __init__(self, skt_peer, global_counter, counter_lock):
        self.socket_peer = Socket(socket_peer=skt_peer)
        self.protocol = ServerProtocol(self.socket_peer)
        self.global_counter = global_counter
        self.counter_lock = counter_lock
        self.sink = os.getenv("SINK")

    def init_client_id(self):
        client_id = self.protocol.recv_auth()
        self.client_id = client_id
        return client_id

    def stop_client(self):
        self.socket_peer.close()
        self.broker.close()
        logging.info("action: client disconnected")

    def get_next_counter(self):
        with self.counter_lock:
            counter = self.global_counter.value
            self.global_counter.value += 1
        return counter

    def start(self):
        self.broker = Broker(tag=f"client{self.client_id}")
        signal.signal(signal.SIGTERM, lambda _n,_f: self.stop_client())
        while True:
            try:
                raw_dto = self.protocol.recv_data_raw(self.client_id)
                if raw_dto is None:
                    break
                raw_dto.set_counter(self.get_next_counter())
                self.broker.public_message(sink=self.sink, message = raw_dto.serialize(), routing_key="default")
            except Exception as e:
                logging.info(f"action: client disconnected")
                break
        self.stop_client()