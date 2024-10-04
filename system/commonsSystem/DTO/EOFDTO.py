import logging
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.DTO import DTO

class EOFDTO(DTO):
    def __init__(self, operation_type = 0, client_id = 0, amount_data = 0, old_operation_type = 0):
        self.operation_type = operation_type #OperationType.OPERATION_TYPE_EOF_INITIAL
        self.client_id = client_id
        self.amount_data = amount_data
        self.old_operation_type = old_operation_type

    #this method only can be used by gateway! no other controllers.
    def set_amount_data_and_type(self, a_amount):
        self.old_operation_type = self.operation_type
        self.operation_type = OperationType.OPERATION_TYPE_EOF_INITIAL
        self.amount_data = a_amount

    def serialize(self):
        eof_bytes = bytearray()
        eof_bytes.extend(self.operation_type.value.to_bytes(1, byteorder='big'))
        eof_bytes.extend(self.old_operation_type.to_bytes(1, byteorder='big'))
        eof_bytes.extend(self.client_id.to_bytes(1, byteorder='big'))
        eof_bytes.extend(self.amount_data.to_bytes(8, byteorder='big'))
        return eof_bytes

    def deserialize(self, data, offset=0):
        logging.info("--------Deserialize a EOF DTO 🌵")
        operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        old_operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        client_id = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        amount_data = int.from_bytes(data[offset:offset+8], byteorder='big')
        offset += 8
        logging.info(f"Deserialize:  gogogos 🅰️ 🅱️")
        return EOFDTO(operation_type, client_id, amount_data, old_operation_type)

