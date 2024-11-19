from common.tolerance.logFile import LogFile
from system.commonsSystem.DTO.RawDTO import RawDTO
import multiprocessing
from multiprocessing import Manager, Array
import logging
import os

class StateHandler:
    _instance = None

    def __init__(self):
        self.result_eofs_by_client = {}
        self.last_batch_by_client = {}
        self.client_handlers = {}
        self.logs = LogFile("gateway")
        self.lock = multiprocessing.Lock()
        self.amount_of_queries = int(os.getenv("AMOUNT_OF_QUERIES", 5))
        manager = Manager()
        self.shared_namespace = manager.Namespace()
        self.shared_namespace.protocols = {}
        self.manager_lock = manager.Lock()
        self.clients_allow = Array('b', [True] * 5)

    def get_instance():
        if StateHandler._instance is None:
            StateHandler._instance = StateHandler()
        return StateHandler._instance

    def add_log(self, bytes):
        with self.lock:
            self.logs.add_log(bytes)
            if self.logs.is_full():
                self.save_checkpoint()

    def last_client_message(self, dto: RawDTO):
        with self.lock:
            self.last_batch_by_client[dto.get_client()] = dto.batch_id
            self.add_log(dto.serialize())

    def add_client_eof(self, client_id, data):
        with self.lock:
            self.add_log(data.serialize())
            if client_id not in self.result_eofs_by_client:
                self.result_eofs_by_client[client_id] = set()
            self.result_eofs_by_client[client_id].add(data.query)
    
    def set_client(self, client_id, clientHandler):
        with self.lock:
            self.client_handlers[client_id] = clientHandler

    def remove_client(self, client_id):
        with self.lock:
            if client_id in self.client_handlers:
                del self.client_handlers[client_id]

    def get_client_id(self):
        with self.lock:
            client_id = self.get_first_available_client()
            logging.info(f"action: get_client_id | client_id: {client_id}")
            if client_id is not None:
                self.set_client_busy(client_id)
                
                return client_id
            else:
                logging.warning("No available client IDs found.")
                return None
    
    def get_batch_id(self, client_id):
        with self.lock:
            return self.last_batch_by_client[client_id]

    def get_first_available_client(self):
        for i in range(len(self.clients_allow)):
            if self.clients_allow[i] and (i+1) not in self.client_handlers:
                return i+1
        return None
    
    def set_client_busy(self, client_id):
        self.clients_allow[client_id] = False

    def set_client_available(self, client_id):
        self.clients_allow[client_id] = True

    def set_protocol(self, client_id, protocol):
        with self.manager_lock:
            protocols = self.shared_namespace.protocols
            protocols[client_id] = protocol
            self.shared_namespace.protocols = protocols

    def send_result_to_client(self, client_id, result):
        with self.manager_lock:
            if client_id not in self.shared_namespace.protocols:
                raise Exception(f"Client {client_id} not found in protocols")
            self.shared_namespace.protocols.get(client_id).send_result(result)

    def is_client_finished(self, client_id):
        with self.lock:
            if client_id not in self.result_eofs_by_client:
                return False
            return len(self.result_eofs_by_client[client_id]) == self.amount_of_queries
        
    def send_eof_to_client(self, client_id):
        with self.manager_lock:
            if client_id not in self.shared_namespace.protocols:
                raise Exception(f"Client {client_id} not found in protocols")
            self.shared_namespace.protocols.get(client_id).send_result(None)
            del self.result_eofs_by_client[client_id]
            del self.client_handlers[client_id]
            with self.lock:
                self.set_client_available(client_id)

    def save_checkpoint(self):
        self.logs.reset()