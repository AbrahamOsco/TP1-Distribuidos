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
import time

class Gateway(Node):
    def __init__(self):
        self.socket_accepter = Socket(port=12345)
        self.result_eofs_by_client = {}
        self.processes = []
        self.running = True
        self.pool_size = 5
        self.amount_of_queries = int(os.getenv("AMOUNT_OF_QUERIES", 5))
        manager = Manager()
        self.shared_namespace = manager.Namespace()
        self.shared_namespace.protocols = {}
        self.manager_lock = manager.Lock()
        self.broker_lock = manager.Lock()
        super().__init__()

    def accept_a_connection(self):
        logging.info("action: Waiting a client to connect | result: pending ⌚")
        socket_peer, addr = self.socket_accepter.accept()
        if socket_peer is None:
            return None
        logging.info("action: Waiting a client to connect | result: success ✅")
        return socket_peer
    
    def start(self):
        self.processes.append(multiprocessing.Process(target=self.run))
        self.processes.append(multiprocessing.Process(target=self.run_server))
        for process in self.processes:
            process.start()
        for process in self.processes:
            process.join()

    def stop_server(self):
        if self.socket_accepter is not None:
            self.socket_accepter.close()
        for process in self.client_processes:
            process.terminate()
            process.join()
        logging.info("action: server stopped | result: success ✅")

    def run_server(self):
        self.client_processes = []
        signal.signal(signal.SIGTERM, lambda _n,_f: self.stop_server())
        semaphore = multiprocessing.Semaphore(self.pool_size)
        while self.running:
            semaphore.acquire()
            socket_peer = self.accept_a_connection()
            if socket_peer is None:
                break
            client_handler = multiprocessing.Process(target=self._handle_client, args=(socket_peer,semaphore))
            client_handler.start()
            self.processes.append(client_handler)
        self.stop_server()

    def abort_client(self, socket_peer):
        socket_peer.close()
        logging.info("action: client disconnected")

    def _handle_client(self, skt_peer, semaphore):
        socket_peer = Socket(socket_peer=skt_peer)
        protocol = ServerProtocol(socket_peer)
        signal.signal(signal.SIGTERM, lambda _n,_f: self.abort_client(socket_peer))
        initialized = False
        while self.running:
            try:
                raw_dto = protocol.recv_data_raw()
                if not initialized:
                    with self.manager_lock:
                        protocols = self.shared_namespace.protocols
                        protocols[raw_dto.get_client()] = protocol
                        self.shared_namespace.protocols = protocols
                    initialized = True
                with self.broker_lock:
                    self.broker.public_message(sink=self.sink, message = raw_dto.serialize(), routing_key="default")
            except Exception as e:
                logging.info(f"action: client disconnected")
                break
        socket_peer.close()
        semaphore.release()
        logging.info("action: exiting client")

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
            self.result_eofs_by_client[client_id] = None
            logging.info(f"action: inform_eof_to_client | client_id: {client_id} | result: success ✅")

    def abort(self):
        for process in self.processes:
            process.terminate()
            process.join()
        logging.info("Gateway abort | result: success ✅")