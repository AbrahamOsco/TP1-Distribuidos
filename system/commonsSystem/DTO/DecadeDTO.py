from system.commonsSystem.DTO.enums.OperationType import OperationType

class DecadeDTO:
    def __init__(self, client_id: int, name: str, year: int, average_playtime: int):
        self.operation_type = OperationType.OPERATION_TYPE_DECADE_DTO
        self.client_id = client_id
        self.name = name
        self.year = year
        self.average_playtime = average_playtime