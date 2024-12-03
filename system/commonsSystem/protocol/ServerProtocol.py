import logging
from common.protocol.Protocol import Protocol
from common.DTO.GameEOFDTO import OPERATION_TYPE_GAMEEOF
from common.DTO.ReviewEOFDTO import OPERATION_TYPE_REVIEWEOF
from system.commonsSystem.DTO.RawDTO import RawDTO
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.EOFDTO import EOFDTO, STATE_DEFAULT
from common.DTO.ResultEOFDTO import OPERATION_TYPE_RESULTSEOF
from common.DTO.Query1ResultDTO import OPERATION_TYPE_QUERY1
from common.DTO.Query2345ResultDTO import OPERATION_TYPE_QUERY2345
from common.DTO.AuthDTO import OPERATION_TYPE_AUTH

class ServerProtocol(Protocol):
    
    def __init__(self, socket):
        super().__init__(socket)

    def recv_auth(self):
        try:
            operation_type = self.recv_number_n_bytes_timeout(1)
            if operation_type != OPERATION_TYPE_AUTH:
                return None
            id_client = self.recv_string()
            logging.info(f"action: recv_auth | client_id: {id_client} ✅")
            return id_client
        except Exception as e:
            return None

    def recv_data_raw(self, client_id):
        operation_type = self.recv_number_n_bytes(1)
        if operation_type == OPERATION_TYPE_AUTH:
            client_id = self.recv_string()
            return client_id
        batch_id = self.recv_number_n_bytes(2)
        if operation_type == OPERATION_TYPE_GAMEEOF:
            return EOFDTO(client=client_id, type=OperationType.OPERATION_TYPE_GAMES_EOF_DTO.value, state=STATE_DEFAULT, batch_id=batch_id)
        if operation_type == OPERATION_TYPE_REVIEWEOF:
            return EOFDTO(client=client_id, type=OperationType.OPERATION_TYPE_REVIEWS_EOF_DTO.value, state=STATE_DEFAULT, batch_id=batch_id)
        list_items_raw = []
        items_amount = self.recv_number_n_bytes(2)
        for _ in range(items_amount):
            element = []
            field_amount = self.recv_number_n_bytes(2)
            for _ in range(field_amount):
                field = self.recv_string()
                element.append(field)
            list_items_raw.append(element)
        return RawDTO(client_id =client_id, type=operation_type, raw_data =list_items_raw, batch_id=batch_id)

    def send_auth_result(self, client_id, batch_id):
        self.send_number_n_bytes(1, OPERATION_TYPE_AUTH)
        self.send_string(client_id)
        self.send_number_n_bytes(2, batch_id)

    def send_result(self, result):
        if result is None:
            self.send_number_n_bytes(1, OPERATION_TYPE_RESULTSEOF)
            return
        self.send_number_n_bytes(1, result.operation_type)
        if result.operation_type == OPERATION_TYPE_QUERY1:
            self.send_number_n_bytes(4, result.windows)
            self.send_number_n_bytes(4, result.linux)
            self.send_number_n_bytes(4, result.mac)
        elif result.operation_type == OPERATION_TYPE_QUERY2345:
            self.send_number_n_bytes(1, result.query)
            self.send_number_n_bytes(2, len(result.games))
            for game in result.games:
                self.send_string(game)
        else:
            raise RuntimeError("action: send_result | result: fail |")