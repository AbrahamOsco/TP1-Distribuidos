from system.commonsSystem.DTO.DTO import DTO
from system.commonsSystem.DTO.enums.OperationType import OperationType

REQUEST_DATA_PARTIAL = 1
RESPONSE_DATA_PARTIAL = 2

class DataPartialDTO(DTO):
    def __init__(self, status = REQUEST_DATA_PARTIAL,):
        self.operation_type = OperationType.OPERATION_TYPE_DATA_PARTIAL_DTO
        self.status = status
    
    def serialize(self):
        calculator_bytes = bytearray()
        calculator_bytes.extend(self.operation_type.value.to_bytes(1, byteorder='big'))
        calculator_bytes.extend(self.status.to_bytes(1, byteorder='big'))
        
        return bytes(calculator_bytes)

    def deserialize(self, data, offset):
        operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset +=1
        status = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset +=1
        
        return DataPartialDTO(status)
