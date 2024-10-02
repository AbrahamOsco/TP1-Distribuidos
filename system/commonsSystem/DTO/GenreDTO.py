from system.commonsSystem.DTO.enums.OperationType import OperationType

class GenreDTO:
    def __init__(self, client_id: int, name: str, gender: str, year: int, average_playtime: int):
        self.operation_type = OperationType.OPERATION_TYPE_GENRE_DTO
        self.client_id = client_id
        self.name = name
        self.gender = gender
        self.year = year
        self.average_playtime = average_playtime