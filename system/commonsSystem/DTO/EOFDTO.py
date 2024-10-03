import logging
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.DTO import DTO

class EOFDTO(DTO):
    def __init__(self, client_id = 0):
        self.operation_type = OperationType.OPERATION_TYPE_EOF_INITIAL
        self.client_id = client_id
    
    def serialize(self):
        eof_bytes = bytearray()
        eof_bytes.extend(self.operation_type.value.to_bytes(1, byteorder='big'))
        eof_bytes.extend(self.client_id.to_bytes(1, byteorder='big'))
        return eof_bytes

    def deserialize(self, data, offset=0):
        operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        client_id = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        return EOFDTO(client_id)

"""    def to_string(self):
        return f"EOF|{self.client}|{int(self.confirmation)}"

    def from_string(data):
        data = data.split("|")
        return EOFDTO(data[1], bool(int(data[2])))
    
    def is_confirmation(self):
        return self.confirmation
    
    def get_client(self):
        return self.client
    
    def is_EOF(self):
        return True
        
"""