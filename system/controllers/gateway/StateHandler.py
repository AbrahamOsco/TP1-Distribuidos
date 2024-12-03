from common.tolerance.logFile import LogFile
from common.tolerance.checkpointFile import CheckpointFile
from system.commonsSystem.DTO.RawDTO import RawDTO
from system.controllers.gateway.gatewayStructure import GatewayStructure, MAX_CLIENTS
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.controllers.gateway.GlobalCounter import GlobalCounter
from multiprocessing import Manager
import logging
import traceback
import os
from cryptography.fernet import Fernet

FERNET_KEY = b'QWGObJry3Q3h3yQs4EZpFMVdRkvxz4QwKqzTbr6p3Ik='
class StateHandler:
    _instance = None

    def __init__(self):
        prefix = os.getenv("NODE_NAME") + os.getenv("NODE_ID") + "_"
        self.amount_of_queries = int(os.getenv("AMOUNT_OF_QUERIES", 5))
        manager = Manager()
        self.shared_namespace = manager.Namespace()
        self.shared_namespace.protocols = {}
        self.shared_namespace.result_eofs_by_client = {}
        self.shared_namespace.last_batch_by_client = {}
        self.shared_namespace.responses_by_client = {}
        self.shared_namespace.logs = LogFile(prefix, remain_open=False)
        self.shared_namespace.clients_allow = [True] * MAX_CLIENTS
        self.manager_lock = manager.Lock()
        self.checkpoint = CheckpointFile(prefix, log_file=self.shared_namespace.logs, id_lists=[])
        self.cipher = Fernet(FERNET_KEY)

    def get_instance():
        if StateHandler._instance is None:
            StateHandler._instance = StateHandler()
        return StateHandler._instance

    def _add_log(self, bytes):
        logs = self.shared_namespace.logs
        logs.add_log(bytes)
        self.shared_namespace.logs = logs
        if self.shared_namespace.logs.is_full():
            self.save_checkpoint()

    def last_client_message(self, dto: RawDTO):
        with self.manager_lock:
            aux = self.shared_namespace.last_batch_by_client
            aux[dto.get_client()] = dto.batch_id
            self.shared_namespace.last_batch_by_client = aux
            self._add_log(dto.serialize())

    def add_client_eof(self, client_id, data):
        with self.manager_lock:
            if data.query == 0:
                logging.info(f"Client {client_id}, global counter {data.global_counter}, {data}")
                return
            self._add_log(data.serialize())
            result_dict = self.shared_namespace.result_eofs_by_client
            if client_id not in result_dict:
                result_dict[client_id] = set()
            result_dict[client_id].add(data.query)
            self.shared_namespace.result_eofs_by_client = result_dict

    def remove_client(self, client_id):
        if client_id in self.shared_namespace.result_eofs_by_client:
            eofs = self.shared_namespace.result_eofs_by_client
            del eofs[client_id]
            self.shared_namespace.result_eofs_by_client = eofs
        if client_id in self.shared_namespace.responses_by_client:
            responses = self.shared_namespace.responses_by_client
            del responses[client_id]
            self.shared_namespace.responses_by_client = responses
        if client_id in self.shared_namespace.last_batch_by_client:
            last_batch = self.shared_namespace.last_batch_by_client
            del last_batch[client_id]
            self.shared_namespace.last_batch_by_client = last_batch
            
    def get_client_id(self):
        with self.manager_lock:
            client_id = self.get_first_available_client()
            logging.info(f"action: get_client_id | client_id: {client_id}")
            if client_id is not None:
                self.set_client_busy(client_id)
                return client_id
            else:
                raise Exception("No clients available")
    
    def get_batch_id(self, client_id):
        with self.manager_lock:
            if client_id not in self.shared_namespace.last_batch_by_client:
                return 0
            return self.shared_namespace.last_batch_by_client[client_id]

    def get_first_available_client(self):
        for i in range(len(self.shared_namespace.clients_allow)):
            if self.shared_namespace.clients_allow[i]:
                return i+1
        return None
    
    def set_client_busy(self, client_id):
        aux = self.shared_namespace.clients_allow
        aux[client_id-1] = False
        self.shared_namespace.clients_allow = aux

    def set_client_available(self, client_id):
        aux = self.shared_namespace.clients_allow
        aux[client_id-1] = True
        self.shared_namespace.clients_allow = aux

    def set_protocol(self, client_id, protocol):
        with self.manager_lock:
            protocols = self.shared_namespace.protocols
            protocols[client_id] = protocol
            self.shared_namespace.protocols = protocols
            self._resend_results(client_id, protocol)

    def _add_result(self, client_id, result):
        responses = self.shared_namespace.responses_by_client
        if client_id not in responses:
            responses[client_id] = []
        responses[client_id].append(result)
        self.shared_namespace.responses_by_client = responses

    def send_result_to_client(self, client_id, data):
        with self.manager_lock:
            self._add_log(data.serialize())
            self._add_result(client_id, data)
            if client_id not in self.shared_namespace.protocols:
                logging.error(f"Client {client_id} not found in protocols")
                return
            result = data.to_result()
            self._send_to_client(client_id, result)

    def is_client_finished(self, client_id):
        with self.manager_lock:
            if client_id not in self.shared_namespace.result_eofs_by_client:
                return False
            logging.info(f"Client {client_id} has finished queries: {self.shared_namespace.result_eofs_by_client[client_id]}")
            return len(self.shared_namespace.result_eofs_by_client[client_id]) == self.amount_of_queries
        
    def send_eof_to_client(self, client_id):
        with self.manager_lock:
            if client_id not in self.shared_namespace.protocols:
                raise Exception(f"Client {client_id} not found in protocols")
            self._send_to_client(client_id, None)
            self.remove_client(client_id)
            self.set_client_available(client_id)
            self.save_checkpoint()

    def _send_to_client(self, client_id, data):
        try:
            self.shared_namespace.protocols.get(client_id).send_result(data)
        except Exception as e:
            logging.error(f"Error sending to client {client_id}: {e}")

    def save_checkpoint(self):
        data = GatewayStructure.to_bytes(self.shared_namespace.result_eofs_by_client, self.shared_namespace.last_batch_by_client, self.shared_namespace.responses_by_client, self.shared_namespace.clients_allow)
        self.checkpoint.save_checkpoint(data)
        self.reset_logs()

    def reset_logs(self):
        logs = self.shared_namespace.logs
        logs.reset()
        self.shared_namespace.logs = logs

    def recover(self):
        try:
            checkpoint, must_reprocess = self.checkpoint.load_checkpoint()
            result_eofs_by_client, last_batch_by_client, responses_by_client, client_allows = GatewayStructure.from_bytes(checkpoint)
            self.shared_namespace.result_eofs_by_client = result_eofs_by_client
            self.shared_namespace.last_batch_by_client = last_batch_by_client
            self.shared_namespace.responses_by_client = responses_by_client
            self.shared_namespace.clients_allow = client_allows
            last_message_by_client = {}
            if must_reprocess:
                logging.info("Reprocessing logs")
                for log in self.shared_namespace.logs.logs:
                    data = DetectDTO(log).get_dto()
                    self.reprocess(data, last_message_by_client)
            self.print_state()
            self.reset_logs()
            self.save_checkpoint()
            return last_message_by_client.values()
        except Exception as e:
            logging.error(f"Error recovering state: {e}")
            traceback.print_exc()
            return []

    def print_state(self):
        for client_id in self.shared_namespace.result_eofs_by_client:
            logging.info(f"Client {client_id} has finished queries: {self.shared_namespace.result_eofs_by_client[client_id]}")
        for client_id in self.shared_namespace.last_batch_by_client:
            logging.info(f"Client {client_id} last batch: {self.shared_namespace.last_batch_by_client[client_id]}")
        for client_id in self.shared_namespace.responses_by_client:
            logging.info(f"Client {client_id} has responses: {self.shared_namespace.responses_by_client[client_id]}")
        for i in range(len(self.shared_namespace.clients_allow)):
            logging.info(f"Client {i+1} is available: {self.shared_namespace.clients_allow[i]}")

    def reprocess(self, data, last_message_by_client):
        client_id = data.get_client()
        if data.is_raw() or (data.is_EOF() and data.query == 0):
            last_message_by_client[client_id] = data
            aux = self.shared_namespace.last_batch_by_client
            aux[client_id] = data.batch_id
            self.shared_namespace.last_batch_by_client = aux
            GlobalCounter.set_current(data.global_counter+1)
            return
        if not data.is_EOF():
            responses = self.shared_namespace.responses_by_client
            if client_id not in responses:
                responses[client_id] = []
            responses[client_id].append(data)
            self.shared_namespace.responses_by_client = responses
            return
        if data.query == 0:
            logging.info(f"Client {client_id}, global counter {data.global_counter}, {data}")
            return
        result_dict = self.shared_namespace.result_eofs_by_client
        if client_id not in result_dict:
            result_dict[client_id] = set()
        result_dict[client_id].add(data.query)
        self.shared_namespace.result_eofs_by_client = result_dict

    def _resend_results(self, client_id, protocol):
        results = self.shared_namespace.responses_by_client.get(client_id, [])
        for data in results:
            result = data.to_result()
            protocol.send_result(result)

    def encrypt_client_id(self, client_id):
        """Encripta el client_id usando la clave simétrica."""
        return self.cipher.encrypt(str(client_id).encode()).decode()

    def decrypt_client_id(self, encrypted_client_id):
        """Desencripta el client_id encriptado."""
        try:
            return int(self.cipher.decrypt(encrypted_client_id.encode()).decode())
        except Exception as e:
            logging.error(f"Error decrypting client_id: {e}")
            return None