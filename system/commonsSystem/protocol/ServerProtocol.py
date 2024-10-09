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
        operation_type = self.recv_number_1_byte()
        client_id = self.recv_number_1_byte()
        if operation_type == OPERATION_TYPE_GAMEEOF:
            amount = self.recv_number_4_bytes()
            return EOFDTO(client=client_id, type=OperationType.OPERATION_TYPE_GAMES_EOF_DTO, state=STATE_DEFAULT, amount_sent=amount)
        if operation_type == OPERATION_TYPE_REVIEWEOF:
            amount = self.recv_number_4_bytes()
            return EOFDTO(client=client_id, type=OperationType.OPERATION_TYPE_REVIEWS_EOF_DTO, state=STATE_DEFAULT, amount_sent=amount)
        list_items_raw = []
        items_amount = self.recv_number_2_bytes()
        for _ in range(items_amount):
            element = []
            field_amount = self.recv_number_2_bytes()
            for _ in range(field_amount):
                field = self.recv_string()
                element.append(field)
            list_items_raw.append(element)
        return RawDTO(client_id =client_id, type=operation_type, raw_data =list_items_raw)

    def send_result(self, result):
        if result is None:
            self.send_number_1_byte(OPERATION_TYPE_RESULTSEOF)
            return
        self.send_number_1_byte(result.operation_type)
        if result.operation_type == OPERATION_TYPE_QUERY1:
            self.send_number_4_bytes(result.windows)
            self.send_number_4_bytes(result.linux)
            self.send_number_4_bytes(result.mac)
        elif result.operation_type == OPERATION_TYPE_QUERY2345:
            self.send_number_1_byte(result.query)
            self.send_number_2_bytes(len(result.games))
            for game in result.games:
                self.send_string(game)
        else:
            raise RuntimeError("action: send_result | result: fail |")