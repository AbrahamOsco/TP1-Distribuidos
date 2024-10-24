from common.protocol.Protocol import Protocol
from common.DTO.GameEOFDTO import OPERATION_TYPE_GAMEEOF
from common.DTO.ReviewEOFDTO import OPERATION_TYPE_REVIEWEOF
from system.commonsSystem.DTO.RawDTO import RawDTO
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.EOFDTO import EOFDTO, STATE_DEFAULT
from common.DTO.ResultEOFDTO import OPERATION_TYPE_RESULTSEOF
from common.DTO.Query1ResultDTO import OPERATION_TYPE_QUERY1
from common.DTO.Query2345ResultDTO import OPERATION_TYPE_QUERY2345

class ServerProtocol(Protocol):
    
    def __init__(self, socket):
        super().__init__(socket)

    def recv_data_raw(self):
        operation_type = self.recv_number_n_bytes(1)
        client_id = self.recv_number_n_bytes(1)
        if operation_type == OPERATION_TYPE_GAMEEOF:
            amount = self.recv_number_n_bytes(4)
            return EOFDTO(client=client_id, type=OperationType.OPERATION_TYPE_GAMES_EOF_DTO.value, state=STATE_DEFAULT, amount_sent=[("default", amount)])
        if operation_type == OPERATION_TYPE_REVIEWEOF:
            amount = self.recv_number_n_bytes(4)
            return EOFDTO(client=client_id, type=OperationType.OPERATION_TYPE_REVIEWS_EOF_DTO.value, state=STATE_DEFAULT, amount_sent=[("default",amount)])
        list_items_raw = []
        items_amount = self.recv_number_n_bytes(2)
        for _ in range(items_amount):
            element = []
            field_amount = self.recv_number_n_bytes(2)
            for _ in range(field_amount):
                field = self.recv_string()
                element.append(field)
            list_items_raw.append(element)
        return RawDTO(client_id =client_id, type=operation_type, raw_data =list_items_raw)

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