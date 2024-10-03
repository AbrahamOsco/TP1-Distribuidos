from system.commonsSystem.DTO.DTO import DTO
from system.commonsSystem.DTO.enums.OperationType import OperationType

class GenreDTO(DTO):
    def __init__(self, client_id: int =0, name: str ="", gender: str ="", year: int =0, average_playtime: int =0):
        self.operation_type = OperationType.OPERATION_TYPE_GENRE_DTO
        self.client_id = client_id
        self.name = name
        self.gender = gender
        self.year = year
        self.average_playtime = average_playtime
        
    def serialize(self):
        genre_bytes = bytearray()
        genre_bytes.extend(self.operation_type.value.to_bytes(1, byteorder='big'))
        genre_bytes.extend(self.client_id.to_bytes(1, byteorder='big'))
        genre_bytes.extend(self.serialize_str(self.name))
        genre_bytes.extend(self.serialize_str(self.gender))
        genre_bytes.extend(self.year.to_bytes(4, byteorder='big'))
        genre_bytes.extend(self.average_playtime.to_bytes(4, byteorder='big'))
        return bytes(genre_bytes)
    
    def deserialize_genreDTO(self, data, offset):
        operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        client_id = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        name, offset = self.deserialize_str(data, offset)
        gender, offset = self.deserialize_str(data, offset)
        year = int.from_bytes(data[offset:offset+4], byteorder='big')
        offset += 4
        average_playtime = int.from_bytes(data[offset:offset+4], byteorder='big')
        offset += 4
        return GenreDTO(client_id=client_id, name=name, gender=gender, year=year, average_playtime=average_playtime), offset