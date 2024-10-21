import logging
import signal
import os
from common.socket.Socket import Socket
from system.commonsSystem.protocol.ServerProtocol import ServerProtocol
from system.commonsSystem.broker.Broker import Broker
from system.controllers.gateway.GlobalCounter import GlobalCounter

class ClientHandler:
    def __init__(self, skt_peer):
        self.socket_peer = Socket(socket_peer=skt_peer)
        self.protocol = ServerProtocol(self.socket_peer)
        self.sink = os.getenv("SINK")

    def init_client_id(self):
        client_id = self.protocol.recv_auth()
        self.client_id = client_id
        return client_id

    def stop_client(self):
        self.socket_peer.close()
        self.broker.close()
        logging.info("action: client disconnected")

    def start(self):
        logging.info("Llegue 6")
        self.broker = Broker(tag=f"client{self.client_id}")
        signal.signal(signal.SIGTERM, lambda _n,_f: self.stop_client())
        logging.info("Llegue 7")
        while True:
            try:
                raw_dto = self.protocol.recv_data_raw(self.client_id)
                if raw_dto is None:
                    break
                logging.info("Llegue 8")
                raw_dto.set_counter(GlobalCounter.get_next())
                logging.info("Llegue 9")
                self.broker.public_message(sink=self.sink, message = raw_dto.serialize(), routing_key="default")
            except Exception as e:
                logging.info(f"action: client disconnected {e}")
                break
        self.stop_client()