from common.utils.utils import ResultType, ALL_GAMES_WAS_SENT, ALL_REVIEWS_WAS_SENT
from common.protocol.Protocol import Protocol
from common.DTO.GamesRawDTO import GamesRawDTO, OPERATION_TYPE_GAMES_RAW
from system.commonsSystem.DTO.EOFDTO import EOFDTO
from common.DTO.ReviewsRawDTO import ReviewsRawDTO
from system.commonsSystem.DTO.enums.OperationType import OperationType


class ServerProtocol(Protocol):
    
    def __init__(self, socket):
        super().__init__(socket) 
        
    def recv_data_raw(self):
        operation_type = self.recv_number_1_byte()
        client_id = self.recv_number_1_byte()
        if operation_type == ALL_GAMES_WAS_SENT or operation_type == ALL_REVIEWS_WAS_SENT:
            return EOFDTO(operation_type =operation_type, client_id =client_id)
        list_items_raw = []
        items_amount = self.recv_number_4_bytes()
        for i in range(items_amount):
            element = []
            field_amount = self.recv_number_2_bytes()
            for j in range(field_amount):
                field = self.recv_string()
                element.append(field)
            list_items_raw.append(element)
        if operation_type == OPERATION_TYPE_GAMES_RAW:
            return GamesRawDTO(client_id =client_id, games_raw =list_items_raw)
        return ReviewsRawDTO(client_id =client_id, reviews_raw =list_items_raw)
    
    def send_result_query(self, resultDTO, result_type):
        self.send_number_1_byte(result_type.value)
        if (result_type == ResultType.RESULT_QUERY_1):
            self.send_number_1_byte(resultDTO.client_id)
            self.send_number_4_bytes(resultDTO.windows)
            self.send_number_4_bytes(resultDTO.linux)
            self.send_number_4_bytes(resultDTO.mac)
        else:
            self.send_number_1_byte(resultDTO.client_id)
            self.send_number_2_bytes(len(resultDTO.data))
            for key, value in resultDTO.data.items():
                self.send_string(key)
                self.send_number_4_bytes(value)
        