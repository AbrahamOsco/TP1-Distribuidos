from system.commonsSystem.DTO.enums.OperationType import OperationType

type_to_length = {
    OperationType.OPERATION_TYPE_SHORT_STR.value: 1,
    OperationType.OPERATION_TYPE_MID_STR.value: 2,
    OperationType.OPERATION_TYPE_LONG_STR.value: 3,
}

class DTO:
    def __init__(self):
        pass
    
    def serialize_str(a_string:str=""):
        serialized_string = bytearray()
        string_in_bytes = a_string.encode('utf-8')
        string_length = len(string_in_bytes)
        if string_length < 256:
            serialized_string.extend(OperationType.OPERATION_TYPE_SHORT_STR.value.to_bytes(1, byteorder='big'))
            serialized_string.extend(string_length.to_bytes(1, byteorder='big'))
        elif string_length < 65536:
            serialized_string.extend(OperationType.OPERATION_TYPE_MID_STR.value.to_bytes(1, byteorder='big'))
            serialized_string.extend(string_length.to_bytes(2, byteorder='big'))
        else:
            serialized_string.extend(OperationType.OPERATION_TYPE_LONG_STR.value.to_bytes(1, byteorder='big'))
            serialized_string.extend(string_length.to_bytes(3, byteorder='big'))
        serialized_string.extend(string_in_bytes)
        return serialized_string

    def deserialize_str(data, offset):
        try:
            operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
            offset += 1
            length_length = type_to_length[operation_type]
            string_length = int.from_bytes(data[offset:offset+length_length], byteorder='big')
            offset += length_length
            string = data[offset:offset + string_length].decode('utf-8')
            offset += string_length
            return string, offset
        except Exception as e:
            return "", offset