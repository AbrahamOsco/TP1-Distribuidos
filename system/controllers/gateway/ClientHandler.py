import logging
import re
import signal
import os
import sys
from common.socket.Socket import Socket
from system.commonsSystem.protocol.ServerProtocol import ServerProtocol
from system.commonsSystem.broker.Broker import Broker
from system.controllers.gateway.GlobalCounter import GlobalCounter

CLIENTS_LOG_PATH = "/data/clients.log"
class ClientHandler:
    def __init__(self, skt_peer):
        self.socket_peer = Socket(socket_peer=skt_peer)
        self.protocol = ServerProtocol(self.socket_peer)
        self.sink = os.getenv("SINK")

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

    def update_client_batch_log(self):
        if os.path.exists(CLIENTS_LOG_PATH):
            with open(CLIENTS_LOG_PATH, "r") as file:
                lines = file.readlines()

            updated_lines = []
            for line in lines:
                if f"Client ID: {self.client_id}," in line:
                    match = re.match(r"Client ID: (\d+), Batch ID: (\d+)", line)
                    if match and int(match.group(1)) == self.client_id:
                        current_batch_id = int(match.group(2))
                        new_batch_id = current_batch_id + 1
                        updated_line = f"Client ID: {self.client_id}, Batch ID: {new_batch_id}\n"
                        updated_lines.append(updated_line)
                    else:
                        updated_lines.append(line)
                else:
                    updated_lines.append(line)

            with open(CLIENTS_LOG_PATH, "w") as file:
                file.writelines(updated_lines)
        else:
            logging.warning(f"action: batch update failed | reason: {CLIENTS_LOG_PATH} not found")


    def start(self):
        self.broker = Broker(tag=f"client{self.client_id}")
        signal.signal(signal.SIGTERM, lambda _n,_f: self.stop_client())
        self.send_auth_confirm()

        while True:
            try:
                raw_dto = self.protocol.recv_data_raw(self.client_id)
                if raw_dto is None:
                    break
                raw_dto.set_counter(GlobalCounter.get_next())
                self.update_client_batch_log()
                self.broker.public_message(sink=self.sink, message = raw_dto.serialize(), routing_key="default")
            except Exception as e:
                logging.info(f"action: client disconnected")
                break
        self.stop_client()