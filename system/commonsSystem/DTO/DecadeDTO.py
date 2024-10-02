from system.commonsSystem.DTO.enums.OperationType import OperationType

class DecadeDTO:
    def __init__(self, client_id: int =0, name: str ="", year: int =0, average_playtime: int =0):
        self.operation_type = OperationType.OPERATION_TYPE_DECADE_DTO
        self.client_id = client_id
        self.name = name
        self.year = year
        self.average_playtime = average_playtime