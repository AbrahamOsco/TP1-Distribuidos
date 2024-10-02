from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.EOFDTO import EOFDTO
from system.commonsSystem.DTO.GameDTO import GameDTO
from system.commonsSystem.DTO.ReviewDTO import ReviewDTO

class DTO:
    def __init__(self):
        pass
    
    def serialize_str(self, a_string:str):
        serialized_string = bytearray()
        string_in_bytes = a_string.encode('utf-8')
        serialized_string.extend(OperationType.OPERATION_TYPE_STR.value.to_bytes(1, byteorder='big'))
        serialized_string.extend(len(string_in_bytes).to_bytes(2, byteorder='big'))
        serialized_string.extend(string_in_bytes)
        return serialized_string

    def deserialize_str(self, data, offset):
        operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        string_length = int.from_bytes(data[offset:offset+2], byteorder='big')
        offset += 2
        string = data[offset:offset + string_length].decode('utf-8')
        offset += string_length
        return string, offset
