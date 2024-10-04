from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.DTO import DTO
from system.commonsSystem.DTO.IndexDTO import IndexDTO

class GamesIndexDTO(IndexDTO):
    def __init__(self, client_id =0, games_raw = [], indexes = {}):
        super().__init__(client_id =client_id, data_raw =games_raw, indexes =indexes)
        self.operation_type = OperationType.OPERATION_TYPE_GAMES_INDEX_DTO

    def get_instance(self, client_id, indexes, items_raw, offset):
        return GamesIndexDTO(client_id =client_id, indexes =indexes, games_raw =items_raw) 
