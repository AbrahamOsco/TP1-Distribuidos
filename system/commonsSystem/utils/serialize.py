import logging
from system.commonsSystem.DTO.enums.OperationType import OperationType


def serialize_str(a_string:str):
    serialized_string = bytearray()
    string_in_bytes = a_string.encode('utf-8')
    serialized_string.extend(OperationType.OPERATION_TYPE_STR.value.to_bytes(1, byteorder='big'))
    serialized_string.extend(len(string_in_bytes).to_bytes(4, byteorder='big'))
    serialized_string.extend(string_in_bytes)
    return serialized_string

def deserialize_str(data, offset):
    operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
    offset += 1
    string_length = int.from_bytes(data[offset:offset+4], byteorder='big')
    offset += 4
    string = data[offset:offset + string_length].decode('utf-8')
    offset += string_length
    return string, offset