from common.socket.Socket import Socket
from system.commonsSystem.node.node import Node
import logging
import multiprocessing
import os
import signal
from multiprocessing import Manager
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.DTO.EOFDTO import EOFDTO
from system.controllers.gateway.ClientHandler import ClientHandler

PORT_SERVER = 12345
MAX_CLIENTS = 5

class Gateway(Node):
    def __init__(self):
        self.socket_accepter = Socket(port =PORT_SERVER)
        self.result_eofs_by_client = {}
        self.running = True
        self.pool_size = MAX_CLIENTS
        self.amount_of_queries = int(os.getenv("AMOUNT_OF_QUERIES", 5))
        manager = Manager()
        self.shared_namespace = manager.Namespace()
        self.shared_namespace.protocols = {}
        self.manager_lock = manager.Lock()
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
        self.pool.close()
        self.pool.join()
        if self.socket_accepter is not None:
            self.socket_accepter.close()
        logging.info("action: server stopped | result: success ✅")

    def run_server(self):
        with multiprocessing.Pool(self.pool_size) as self.pool:
            signal.signal(signal.SIGTERM, lambda _n,_f: self.stop_server())
            while self.running:
                socket_peer = self.accept_a_connection()
                if socket_peer is None:
                    break
                client_handler = ClientHandler(socket_peer)
                client_id = client_handler.init_client_id()
                if client_id is None:
                    continue
                with self.manager_lock:
                    protocols = self.shared_namespace.protocols
                    protocols[client_id] = client_handler.protocol
                    self.shared_namespace.protocols = protocols
                self.pool.apply_async(func = client_handler.start, args = (), error_callback = lambda e: logging.error(f"action: error | result: {e}"))
            self.stop_server()

    def process_data(self, data: GamesDTO):
        result = data.to_result()
        with self.manager_lock:
            self.shared_namespace.protocols.get(data.get_client()).send_result(result)

    def inform_eof_to_nodes(self, data: EOFDTO):
        client_id = data.get_client()
        if client_id not in self.result_eofs_by_client:
            self.result_eofs_by_client[client_id] = 0
        self.result_eofs_by_client[client_id] += 1
        if self.result_eofs_by_client[client_id] == self.amount_of_queries:
            with self.manager_lock:
               self.shared_namespace.protocols.get(data.get_client()).send_result(None)
            del self.result_eofs_by_client[client_id]
            logging.info(f"action: inform_eof_to_client | client_id: {client_id} | result: success ✅")

    def stop(self):
        self.broker.close()
        self.listener_proc.terminate()
        self.listener_proc.join()
        logging.info("Gateway abort | result: success ✅")