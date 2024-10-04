from system.commonsSystem.DTO.DTO import DTO
from system.commonsSystem.DTO.enums.OperationType import OperationType

class GrouperTopAveragePlayTimeDTO(DTO):
    def __init__(self, client_id: int =0, name: str="", average_playtime: int=0):
        self.operation_type = OperationType.OPERATION_TYPE_GROUPER_TOP_AVERAGE_PLAYTIME_DTO
        self.client_id = client_id
        self.name = name
        self.average_playtime = average_playtime

    def serialize(self):
        top_average_playtime_bytes = bytearray()
        top_average_playtime_bytes.extend(self.operation_type.value.to_bytes(1, byteorder='big'))
        top_average_playtime_bytes.extend(self.client_id.to_bytes(1, byteorder='big'))
        top_average_playtime_bytes.extend(self.serialize_str(self.name))
        top_average_playtime_bytes.extend(self.average_playtime.to_bytes(8, byteorder='big'))
        return bytes(top_average_playtime_bytes)
    
    def deserialize(self, data, offset):
        operation_tpe = int.from_bytes(data[offset:offset + 1], byteorder='big')
        offset += 1
        client_id = int.from_bytes(data[offset:offset + 1], byteorder='big')
        offset += 1
        name, offset = self.deserialize_str(data, offset)
        average_playtime = int.from_bytes(data[offset:offset + 8], byteorder='big')
        offset += 8
        return GrouperTopAveragePlayTimeDTO(client_id =client_id, name=name, average_playtime=average_playtime ), offset
    