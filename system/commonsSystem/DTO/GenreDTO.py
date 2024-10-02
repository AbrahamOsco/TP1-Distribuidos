from system.commonsSystem.DTO.enums.OperationType import OperationType

class GenreDTO:
    def __init__(self, client_id: int =0, name: str ="", gender: str ="", year: int =0, average_playtime: int =0):
        self.operation_type = OperationType.OPERATION_TYPE_GENRE_DTO
        self.client_id = client_id
        self.name = name
        self.gender = gender
        self.year = year
        self.average_playtime = average_playtime