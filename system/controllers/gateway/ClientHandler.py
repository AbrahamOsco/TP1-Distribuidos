import logging
import signal
import os
import sys
from common.socket.Socket import Socket
from system.commonsSystem.protocol.ServerProtocol import ServerProtocol
from system.commonsSystem.broker.Broker import Broker
from system.controllers.gateway.GlobalCounter import GlobalCounter
from system.controllers.gateway.StateHandler import StateHandler

CLIENTS_LOG_PATH = "/data/clients.log"
class ClientHandler:
    def __init__(self, skt_peer):
        self.socket_peer = Socket(socket_peer=skt_peer)
        self.protocol = ServerProtocol(self.socket_peer)
        self.sink = os.getenv("SINK")
        self.batch_id = 0

    def recv_auth(self):
        return self.protocol.recv_auth()

    def set_client_id(self, client_id):
        self.client_id = client_id

    def set_batch_id(self, batch_id):
        self.batch_id = batch_id

    def stop_client(self):
        self.socket_peer.close()
        self.broker.close()
        logging.info("action: client disconnected")
        sys.exit(0)

    def send_auth_confirm(self):
        logging.info(f"action: auth confirm | client_id: {self.client_id} | batch_id: {self.batch_id}")
        self.protocol.send_auth_result(self.client_id, self.batch_id)

    def start(self):
        self.broker = Broker(tag=f"client{self.client_id}")
        signal.signal(signal.SIGTERM, lambda _n,_f: self.stop_client())
        self.send_auth_confirm()
        self.state_handler = StateHandler.get_instance()
        self.state_handler.resend_results(self.client_id)

        if self.state_handler.is_client_finished(self.client_id):
            logging.info(f"action: client already finished")
            self.state_handler.send_eof_to_client(self.client_id)
            self.stop_client()
            return

        while True:
            try:
                raw_dto = self.protocol.recv_data_raw(self.client_id)
                if raw_dto is None:
                    break
                if raw_dto.batch_id <= self.batch_id:
                    logging.info(f"action: client already processed batch | batch_id: {raw_dto.batch_id}")
                    continue
                self.batch_id = raw_dto.batch_id
                raw_dto.set_counter(GlobalCounter.get_next())
                self.state_handler.last_client_message(raw_dto)
                self.broker.public_message(sink=self.sink, message = raw_dto.serialize(), routing_key="default")
            except Exception as e:
                logging.info(f"action: client disconnected")
                break
        self.stop_client()