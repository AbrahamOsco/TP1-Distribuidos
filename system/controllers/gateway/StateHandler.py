from common.tolerance.logFile import LogFile
from common.tolerance.checkpointFile import CheckpointFile
from system.commonsSystem.DTO.RawDTO import RawDTO
from system.controllers.gateway.gatewayStructure import GatewayStructure
from system.commonsSystem.DTO.DetectDTO import DetectDTO
import multiprocessing
from multiprocessing import Manager
import logging
import os

class StateHandler:
    _instance = None

    def __init__(self):
        self.lock = multiprocessing.Lock()
        prefix = os.getenv("NODE_NAME") + os.getenv("NODE_ID") + "_"
        self.amount_of_queries = int(os.getenv("AMOUNT_OF_QUERIES", 5))
        manager = Manager()
        self.shared_namespace = manager.Namespace()
        self.shared_namespace.protocols = {}
        self.shared_namespace.result_eofs_by_client = {}
        self.shared_namespace.client_handlers = {}
        self.shared_namespace.last_batch_by_client = {}
        self.shared_namespace.responses_by_client = {}
        self.shared_namespace.logs = LogFile(prefix, remain_open=False)
        self.shared_namespace.clients_allow = [True] * 5
        self.manager_lock = manager.Lock()
        self.checkpoint = CheckpointFile(prefix, log_file=self.shared_namespace.logs, id_lists=[])
        self.recover()

    def get_instance():
        if StateHandler._instance is None:
            StateHandler._instance = StateHandler()
        return StateHandler._instance

    def _add_log(self, bytes):
        self.shared_namespace.logs.add_log(bytes)
        if self.shared_namespace.logs.is_full():
            self.save_checkpoint()

    def last_client_message(self, dto: RawDTO):
        with self.lock:
            self.shared_namespace.last_batch_by_client[dto.get_client()] = dto.batch_id
            self._add_log(dto.serialize())

    def add_client_eof(self, client_id, data):
        with self.lock:
            self._add_log(data.serialize())
            result_dict = self.shared_namespace.result_eofs_by_client
            if client_id not in result_dict:
                result_dict[client_id] = set()
            result_dict[client_id].add(data.query)
            self.shared_namespace.result_eofs_by_client = result_dict
    
    def set_client(self, client_id, clientHandler):
        with self.manager_lock:
            handlers = self.shared_namespace.client_handlers
            handlers[client_id] = clientHandler
            self.shared_namespace.client_handlers = handlers

    def remove_client(self, client_id):
        if client_id in self.shared_namespace.client_handlers:
            handlers = self.shared_namespace.client_handlers
            del handlers[client_id]
            self.shared_namespace.client_handlers = handlers
        if client_id in self.shared_namespace.result_eofs_by_client:
            eofs = self.shared_namespace.result_eofs_by_client
            del eofs[client_id]
            self.shared_namespace.result_eofs_by_client = eofs
        if client_id in self.shared_namespace.responses_by_client:
            responses = self.shared_namespace.responses_by_client
            del responses[client_id]
            self.shared_namespace.responses_by_client = responses

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
            return self.shared_namespace.last_batch_by_client[client_id]

    def get_first_available_client(self):
        for i in range(len(self.shared_namespace.clients_allow)):
            if self.shared_namespace.clients_allow[i] and (i+1) not in self.shared_namespace.client_handlers:
                return i+1
        return None
    
    def set_client_busy(self, client_id):
        aux = self.shared_namespace.clients_allow
        aux[client_id] = False
        self.shared_namespace.clients_allow = aux

    def set_client_available(self, client_id):
        aux = self.shared_namespace.clients_allow
        aux[client_id] = True
        self.shared_namespace.clients_allow = aux

    def set_protocol(self, client_id, protocol):
        with self.manager_lock:
            protocols = self.shared_namespace.protocols
            protocols[client_id] = protocol
            self.shared_namespace.protocols = protocols

    def _add_result(self, client_id, result):
        with self.lock:
            responses = self.shared_namespace.responses_by_client
            if client_id not in responses:
                responses[client_id] = []
            responses[client_id].append(result)
            self.shared_namespace.responses_by_client = responses

    def send_result_to_client(self, client_id, data):
        with self.manager_lock:
            if client_id not in self.shared_namespace.protocols:
                raise Exception(f"Client {client_id} not found in protocols")
            self._add_log(data.serialize())
            self._add_result(client_id, data)
            result = data.to_result()
            self.shared_namespace.protocols.get(client_id).send_result(result)

    def is_client_finished(self, client_id):
        with self.lock:
            if client_id not in self.shared_namespace.result_eofs_by_client:
                return False
            return len(self.shared_namespace.result_eofs_by_client[client_id]) == self.amount_of_queries
        
    def send_eof_to_client(self, client_id):
        with self.manager_lock:
            if client_id not in self.shared_namespace.protocols:
                raise Exception(f"Client {client_id} not found in protocols")
            self.shared_namespace.protocols.get(client_id).send_result(None)
            self.remove_client(client_id)
            with self.lock:
                self.set_client_available(client_id)
                self.save_checkpoint()

    def save_checkpoint(self):
        data = GatewayStructure.to_bytes(self.shared_namespace.result_eofs_by_client, self.shared_namespace.last_batch_by_client, self.shared_namespace.responses_by_client, self.shared_namespace.clients_allow)
        self.checkpoint.save_checkpoint(data)

    def recover(self):
        checkpoint, must_reprocess = self.checkpoint.load_checkpoint()
        self.data.from_bytes(checkpoint)
        if must_reprocess:
            for log in self.shared_namespace.logs:
                data = DetectDTO(log).get_dto()
                pass# CHANGE THIS
        self.print_state()
        self.save_checkpoint()

    def print_state():
        pass