from common.protocol.Protocol import Protocol
from common.DTO.GameEOFDTO import OPERATION_TYPE_GAMEEOF
from common.DTO.ReviewEOFDTO import OPERATION_TYPE_REVIEWEOF
from common.DTO.Query1ResultDTO import Query1ResultDTO, OPERATION_TYPE_QUERY1
from common.DTO.Query2345ResultDTO import Query2345ResultDTO, OPERATION_TYPE_QUERY2345
from common.DTO.ResultEOFDTO import OPERATION_TYPE_RESULTSEOF
import logging

class ClientProtocol(Protocol):
    
    def __init__(self, a_id, socket):
        self.id = a_id
        super().__init__(socket)  #uso super para invocar al constructor del padre. 
        self.getResult = {
            OPERATION_TYPE_QUERY1: self.get_query1,
            OPERATION_TYPE_QUERY2345: self.get_query2345,
        }

# [ ["1", "3", "abcasda", "1", "0"], ["2", "4", "abc", "-1", "0"], ... ] 
    def send_data_raw(self, data_raw_dto):
        self.send_number_1_byte(data_raw_dto.operation_type)
        self.send_number_1_byte(self.id) 
        self.send_number_2_bytes(len(data_raw_dto.data_raw))
        for item in data_raw_dto.data_raw:
            self.send_number_2_bytes(len(item))
            for field in item:
                self.send_string(field)

    def send_games_eof(self, amount):
        self.send_number_1_byte(OPERATION_TYPE_GAMEEOF)
        self.send_number_1_byte(self.id)
        self.send_number_4_bytes(amount)
        logging.info(f"Games EOF sent, AMOUNT: {amount}")

    def send_reviews_eof(self, amount):
        self.send_number_1_byte(OPERATION_TYPE_REVIEWEOF)
        self.send_number_1_byte(self.id)
        self.send_number_4_bytes(amount)

    def recv_result(self):
        operation_type = self.recv_number_1_byte()
        if operation_type == OPERATION_TYPE_RESULTSEOF:
            return None
        if operation_type not in self.getResult:
            logging.error(f"Unknown operation type: {operation_type}")
            logging.info(f"Operation types: {self.getResult.keys()}")
            return None
        return self.getResult[operation_type]()
    
    def get_query1(self):
        windows = self.recv_number_4_bytes()
        linux = self.recv_number_4_bytes()
        mac = self.recv_number_4_bytes()
        return Query1ResultDTO(windows, linux, mac)
    
    def get_query2345(self):
        query = self.recv_number_1_byte()
        amount = self.recv_number_2_bytes()
        games = []
        for _ in range (amount):
            game = self.recv_string()
            games.append(game)
        return Query2345ResultDTO(query, games)