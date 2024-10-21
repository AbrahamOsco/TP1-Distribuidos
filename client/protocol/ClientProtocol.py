from common.protocol.Protocol import Protocol
from common.DTO.GameEOFDTO import OPERATION_TYPE_GAMEEOF
from common.DTO.ReviewEOFDTO import OPERATION_TYPE_REVIEWEOF
from common.DTO.Query1ResultDTO import Query1ResultDTO, OPERATION_TYPE_QUERY1
from common.DTO.Query2345ResultDTO import Query2345ResultDTO, OPERATION_TYPE_QUERY2345
from common.DTO.ResultEOFDTO import OPERATION_TYPE_RESULTSEOF
from common.DTO.AuthDTO import OPERATION_TYPE_AUTH
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
        self.send_number_n_bytes(1, data_raw_dto.operation_type)
        self.send_number_n_bytes(2, len(data_raw_dto.data_raw))
        self.send_number_n_bytes(2, data_raw_dto.batch_id)
        for item in data_raw_dto.data_raw:
            self.send_number_n_bytes(2, len(item))
            for field in item:
                self.send_string(field)

    def send_games_eof(self, batch_id):
        self.send_number_n_bytes(1, OPERATION_TYPE_GAMEEOF)
        self.send_number_n_bytes(2, batch_id)

    def send_reviews_eof(self, batch_id):
        self.send_number_n_bytes(1, OPERATION_TYPE_REVIEWEOF)
        self.send_number_n_bytes(2, batch_id)

    def send_auth(self):
        self.send_number_n_bytes(1, OPERATION_TYPE_AUTH)
        self.send_number_n_bytes(1, self.id)

    def recv_result(self):
        operation_type = self.recv_number_n_bytes(1)
        if operation_type == OPERATION_TYPE_RESULTSEOF:
            return None
        if operation_type not in self.getResult:
            logging.error(f"Unknown operation type: {operation_type}")
            logging.info(f"Operation types: {self.getResult.keys()}")
            return None
        return self.getResult[operation_type]()
    
    def get_query1(self):
        windows = self.recv_number_n_bytes(4)
        linux = self.recv_number_n_bytes(4)
        mac = self.recv_number_n_bytes(4)
        return Query1ResultDTO(windows, linux, mac)
    
    def get_query2345(self):
        query = self.recv_number_n_bytes(1)
        amount = self.recv_number_n_bytes(2)
        games = []
        for _ in range (amount):
            game = self.recv_string()
            games.append(game)
        return Query2345ResultDTO(query, games)