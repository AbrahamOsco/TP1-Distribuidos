import logging
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.DTO import DTO

class EOFDTO(DTO):

    def __init__(self, operation_type = 0, client_id = 0, amount_data = 0, old_operation_type = 0):
        self.operation_type = operation_type #OperationType.OPERATION_TYPE_EOF_INITIAL
        self.client_id = client_id
        self.amount_data = amount_data
        self.old_operation_type = old_operation_type

    @classmethod
    def create(cls, eofDTO):
        return EOFDTO(eofDTO.operation_type, eofDTO.client_id, eofDTO.amount_data, eofDTO.old_operation_type)

    def load(self, a_eof_dto):
        self.operation_type = a_eof_dto.operation_type
        self.amount_data = a_eof_dto.amount_data
        self.client_id = a_eof_dto.client_id
        self.old_operation_type = a_eof_dto.old_operation_type
        return EOFDTO(self.operation_type, self.client_id, self.amount_data, self.old_operation_type)
    
    #this method only can be used by gateway! no other controllers. Old Operation tendra ALL_GAMES_SENT o ALL_REVIEWS_SENT y operation type el normal.
    def set_amount_data_and_type(self, a_amount):
        self.old_operation_type = self.operation_type
        self.operation_type = OperationType.OPERATION_TYPE_EOF_INITIAL_DTO
        self.amount_data = a_amount

    def serialize(self):
        eof_bytes = bytearray()
        eof_bytes.extend(self.operation_type.value.to_bytes(1, byteorder='big'))
        eof_bytes.extend(self.old_operation_type.to_bytes(1, byteorder='big'))
        eof_bytes.extend(self.client_id.to_bytes(1, byteorder='big'))
        eof_bytes.extend(self.amount_data.to_bytes(8, byteorder='big'))
        return eof_bytes

    def deserialize(self, data, offset=0):
        operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        old_operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        client_id = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        amount_data = int.from_bytes(data[offset:offset+8], byteorder='big')
        offset += 8
        return EOFDTO(OperationType.OPERATION_TYPE_EOF_INITIAL_DTO, client_id, amount_data, old_operation_type)

