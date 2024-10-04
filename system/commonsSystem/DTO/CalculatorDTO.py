from system.commonsSystem.DTO.DTO import DTO
from system.commonsSystem.DTO.enums.OperationType import OperationType

STATUS_REQUEST = 1
STATUS_RESPONSE = 2

class CalculatorDTO(DTO):
    def __init__(self, client_id: int = 0, status :int = STATUS_REQUEST, amount_data:int = 0 ):
        self.operation_type = OperationType.OPERATION_TYPE_CALCULATOR_DTO
        self.client_id = client_id
        self.status = status
        self.amount_data = amount_data
    
    def serialize(self):
        calculator_bytes = bytearray()
        calculator_bytes.extend(self.operation_type.value.to_bytes(1, byteorder='big'))
        calculator_bytes.extend(self.client_id.to_bytes(1, byteorder='big'))
        calculator_bytes.extend(self.status.to_bytes(1, byteorder='big'))
        calculator_bytes.extend(self.amount_data.to_bytes(8, byteorder='big'))
        return bytes(calculator_bytes)

    def deserialize(self, data, offset):
        operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        client_id = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        status = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        amount_data = int.from_bytes(data[offset:offset+8], byteorder='big')
        offset += 8
        return CalculatorDTO(client_id, status, amount_data)
