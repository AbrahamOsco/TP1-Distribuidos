from common.utils.utils import ResultType, ALL_DATA_WAS_SENT
from common.protocol.Protocol import Protocol
from common.DTO.GamesRawDTO import GamesRawDTO, OPERATION_TYPE_GAMES_RAW
from common.DTO.ReviewsRawDTO import ReviewsRawDTO

class ServerProtocol(Protocol):
    
    def __init__(self, socket):
        super().__init__(socket)  #uso super para invocar al constructor del padre. 

    def recv_data_raw(self):
        operation_type = self.recv_number_1_byte()
        if operation_type == ALL_DATA_WAS_SENT:
            return operation_type  
        client_id = self.recv_number_1_byte()
        list_items_raw = []
        items_amount = self.recv_number_2_bytes()
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
    
    def send_platform_q1(self, platformDTO):
        self.send_number_1_byte(ResultType.RESULT_QUERY_1.value)
        self.send_number_1_byte(platformDTO.client_id)
        self.send_number_4_bytes(platformDTO.windows)
        self.send_number_4_bytes(platformDTO.linux)
        self.send_number_4_bytes(platformDTO.mac)
    