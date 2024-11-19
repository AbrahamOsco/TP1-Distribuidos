import re
from common.socket.Socket import Socket
from system.commonsSystem.node.node import Node
import logging
import multiprocessing
import os
import signal
import sys
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.DTO.EOFDTO import EOFDTO
from system.controllers.gateway.ClientHandler import ClientHandler
from system.controllers.gateway.StateHandler import StateHandler

PORT_SERVER = 12345
MAX_CLIENTS = 5
CLIENT_NOT_FOUND = 0
class Gateway(Node):
    def __init__(self):
        self.socket_accepter = Socket(port =PORT_SERVER)
        self.running = True
        self.pool_size = MAX_CLIENTS
        self.state_handler = StateHandler.get_instance()
        super().__init__()
        
    def accept_a_connection(self):
        logging.info("action: Waiting a client to connect | result: pending ⌚")
        socket_peer, addr = self.socket_accepter.accept()
        if socket_peer is None:
            return None
        logging.info("action: Waiting a client to connect | result: success ✅")
        return socket_peer
    
    def start(self):
        self.listener_proc = multiprocessing.Process(target=self.run_server)
        self.listener_proc.start()
        self.run()
        self.listener_proc.terminate()
        self.listener_proc.join()

    def stop_server(self):
        self.pool.terminate()
        if self.socket_accepter is not None:
            self.socket_accepter.close()
        logging.info("action: server stopped | result: success ✅")

    def run_server(self):
        with multiprocessing.Pool(self.pool_size) as self.pool:
            signal.signal(signal.SIGTERM, lambda _n,_f: self.stop_server())
            while self.running:
                try:
                    socket_peer = self.accept_a_connection()
                    if socket_peer is None:
                        break
                    client_handler = ClientHandler(socket_peer)
                    client_id = client_handler.recv_auth()
                    if client_id == None:
                        socket_peer.close()
                        continue
                    if client_id == CLIENT_NOT_FOUND:
                        logging.info("action: auth without client_id")
                        client_id = self.state_handler.get_client_id()
                        client_handler.set_client_id(client_id)
                    else:
                        logging.info(f"action: auth with client_id | client_id: {client_id}")
                        client_handler.set_client_id(client_id)
                        batch_id = self.state_handler.get_batch_id(client_id)
                        client_handler.set_batch_id(batch_id)
                    self.state_handler.set_protocol(client_id, client_handler.protocol)
                    self.state_handler.set_client(client_id, client_handler)
                    self.pool.apply_async(func = client_handler.start, args = (), error_callback = lambda e: logging.error(f"action: error | result: {e}"))
                except Exception as e:
                    logging.error(f"action: error on incoming connection | result: {e}")
            logging.info("Llegue al server stop")
            self.stop_server()

    def process_data(self, data: GamesDTO):
        self.state_handler.send_result_to_client(data.get_client(), data)

    def inform_eof_to_nodes(self, data: EOFDTO, delivery_tag: str):
        client_id = data.get_client()
        self.state_handler.add_client_eof(client_id, data)
        if self.state_handler.is_client_finished(client_id):
            self.state_handler.send_eof_to_client(client_id)
            logging.info(f"action: inform_eof_to_client | client_id: {client_id} | result: success ✅")
        self.broker.basic_ack(delivery_tag)

    def stop(self):
        logging.info("Gateway abort | result: in progress ⌚")
        self.broker.close()
        self.listener_proc.terminate()
        self.listener_proc.join()
        logging.info("Gateway abort | result: success ✅")
        sys.exit(0)
