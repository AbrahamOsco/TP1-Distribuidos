from system.commonsSystem.DTO.DTO import DTO
from system.commonsSystem.DTO.enums.OperationType import OperationType

STATE_DEFAULT = 1
STATE_COMMIT = 2 ## Informa a los hermanos que llegó un eof y le pide sus cantidades
STATE_OK = 3 ## Informa sus cantidades
STATE_FINISH = 4 ## Informa que terminó y que el cliente debe ser eliminado de memoria

class EOFDTO:
    def __init__(self, type, client:int, state:int, attribute="", amount_received = 0, amount_sent = 0):
        self.operation_type = type
        self.state = state
        self.client = client
        self.attribute = attribute
        self.amount_sent = amount_sent
        self.amount_received = amount_received
    
    def is_ok(self):
        return self.state == STATE_OK

    def is_commit(self):
        return self.state == STATE_COMMIT
    
    def is_finish(self):
        return self.state == STATE_FINISH

    def set_state(self, state):
        self.state = state

    def get_client(self):
        return self.client
    
    def is_EOF(self):
        return True

    def get_type(self):
        if self.operation_type == OperationType.OPERATION_TYPE_GAMES_EOF_DTO.value:
            return "games"
        return "reviews"
    
    def get_amount_received(self):
        return self.amount_received
    
    def get_amount_sent(self):
        return self.amount_sent
    
    def serialize(self):
        eof_bytes = bytearray()
        eof_bytes.extend(self.operation_type.to_bytes(1, byteorder='big'))
        eof_bytes.extend(self.client.to_bytes(1, byteorder='big'))
        eof_bytes.extend(self.state.to_bytes(1, byteorder='big'))
        eof_bytes.extend(DTO.serialize_str(self.attribute))
        eof_bytes.extend(self.amount_received.to_bytes(4, byteorder='big'))
        eof_bytes.extend(self.amount_sent.to_bytes(4, byteorder='big'))
        return bytes(eof_bytes)
    
    def deserialize(data, offset):
        offset -= 1
        operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        client = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        state = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        attribute, offset = DTO.deserialize_str(data, offset)
        amount_received = int.from_bytes(data[offset:offset+4], byteorder='big')
        offset += 4
        amount_sent = int.from_bytes(data[offset:offset+4], byteorder='big')
        offset += 4
        return EOFDTO(operation_type, client, state, attribute, amount_received, amount_sent), offset