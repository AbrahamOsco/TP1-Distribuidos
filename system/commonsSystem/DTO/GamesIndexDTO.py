from system.commonsSystem.DTO.enums.OperationType import OperationType


class GamesIndexDTO:
    def __init__(self, client_id =0, games_raw = [], indexes = {}):
        self.operation_type = OperationType.OPERATION_TYPE_GAMES_INDEX_DTO
        self.client_id = client_id
        self.indexes = indexes
        self.data_raw = games_raw
        


