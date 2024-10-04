from system.commonsSystem.DTO.DTO import DTO
from system.commonsSystem.DTO.enums.OperationType import OperationType

class SelectQ2345DTO(DTO):
    def __init__(self, client_id: int = 0, game_id: int = 0, name: str = "", gender: str = "", year: str = "", average_playtime: int = 0):
        super().__init__()
        self.operation_type = OperationType.OPERATION_TYPE_SELECT_Q2345_DTO
        self.client_id = client_id
        self.game_id = game_id
        self.name = name
        self.gender = gender
        self.year = year
        self.average_playtime = average_playtime

    def serialize(self):
        selectq2345_bytes = bytearray()
        selectq2345_bytes.extend(self.operation_type.value.to_bytes(1, byteorder='big'))
        selectq2345_bytes.extend(self.client_id.to_bytes(1, byteorder='big'))
        selectq2345_bytes.extend(self.game_id.to_bytes(4, byteorder='big'))
        selectq2345_bytes.extend(self.serialize_str(self.name))
        selectq2345_bytes.extend(self.serialize_str(self.gender))
        selectq2345_bytes.extend(self.serialize_str(self.year))
        selectq2345_bytes.extend(self.average_playtime.to_bytes(4, byteorder='big'))
        return bytes(selectq2345_bytes)

    def deserialize_genreDTO(self, data, offset):
        operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        client_id = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 4
        game_id = int.from_bytes(data[offset:offset+4], byteorder='big')
        offset += 4
        name, offset = self.deserialize_str(data, offset)
        gender, offset = self.deserialize_str(data, offset)
        year, offset = self.deserialize_str(data, offset)
        average_playtime = int.from_bytes(data[offset:offset+4], byteorder='big')
        offset += 4
        return SelectQ2345DTO(client_id=client_id, game_id=game_id, name=name, gender=gender, year=year, average_playtime=average_playtime), offset
