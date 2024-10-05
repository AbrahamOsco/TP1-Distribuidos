from common.protocol.Protocol import Protocol
from common.DTO.GameEOFDTO import OPERATION_TYPE_GAMEEOF
from common.DTO.ReviewEOFDTO import OPERATION_TYPE_REVIEWEOF

class ClientProtocol(Protocol):
    
    def __init__(self, a_id, socket):
        self.id = a_id
        super().__init__(socket)  #uso super para invocar al constructor del padre. 

# [ ["1", "3", "abcasda", "1", "0"], ["2", "4", "abc", "-1", "0"], ... ] 
    def send_data_raw(self, data_raw_dto):
        self.send_number_1_byte(data_raw_dto.operation_type)
        self.send_number_1_byte(self.id) 
        self.send_number_2_bytes(len(data_raw_dto.data_raw))
        for item in data_raw_dto.data_raw:
            self.send_number_2_bytes(len(item))
            for field in item:
                self.send_string(field)

    def send_games_eof(self):
        self.send_number_1_byte(OPERATION_TYPE_GAMEEOF)
        self.send_number_1_byte(self.id)

    def send_reviews_eof(self):
        self.send_number_1_byte(OPERATION_TYPE_REVIEWEOF)
        self.send_number_1_byte(self.id)

