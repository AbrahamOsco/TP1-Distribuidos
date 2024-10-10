from common.socket.Socket import Socket
from system.commonsSystem.node.node import Node
import logging
import multiprocessing
import os
import signal
from multiprocessing import Manager
from system.commonsSystem.protocol.ServerProtocol import ServerProtocol
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.DTO.EOFDTO import EOFDTO

class Gateway(Node):
    def __init__(self):
        self.socket_accepter = Socket(port=12345)
        self.result_eofs_by_client = {}
        self.processes = []
        self.amount_of_queries = int(os.getenv("AMOUNT_OF_QUERIES", 5))
        manager = Manager()
        self.shared_namespace = manager.Namespace()
        super().__init__()

    def accept_a_connection(self):
        logging.info("action: Waiting a client to connect | result: pending ⌚")
        self.socket_peer, addr = self.socket_accepter.accept()
        logging.info("action: Waiting a client to connect | result: success ✅")
        self.shared_namespace.protocol = ServerProtocol(self.socket_peer)
    
    def start(self):
        self.processes.append(multiprocessing.Process(target=self.run))
        self.processes.append(multiprocessing.Process(target=self.run_server))
        for process in self.processes:
            process.start()
        for process in self.processes:
            process.join()

    def stop_server(self):
        self.socket_peer.close()
        self.socket_accepter.close()
        logging.info("action: server stopped | result: success ✅")

    def run_server(self):
        signal.signal(signal.SIGTERM, lambda _n,_f: self.stop_sever())
        while True:
            self.accept_a_connection()
            while True:
                try:
                    raw_dto = self.shared_namespace.protocol.recv_data_raw()
                    self.broker.public_message(sink=self.sink, message = raw_dto.serialize(), routing_key="default")
                except Exception as e:
                    logging.info(f"action: client disconnected")
                    break

    def process_data(self, data: GamesDTO):
        result = data.to_result()
        self.shared_namespace.protocol.send_result(result)

    def inform_eof_to_nodes(self, data: EOFDTO):
        client_id = data.get_client()
        if client_id not in self.result_eofs_by_client:
            self.result_eofs_by_client[client_id] = 0
        self.result_eofs_by_client[client_id] += 1
        if self.result_eofs_by_client[client_id] == self.amount_of_queries:
            self.shared_namespace.protocol.send_result(None)
            self.result_eofs_by_client[client_id] = None
            logging.info(f"action: inform_eof_to_client | client_id: {client_id} | result: success ✅")

    def abort(self):
        self.stop()
        logging.info("action: broker stop | result: success ✅")
        for process in self.processes:
            process.terminate()
            process.join()
        logging.info("Gateway abort | result: success ✅")