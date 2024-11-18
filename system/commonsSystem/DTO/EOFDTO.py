from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.BatchDTO import BatchDTO

STATE_DEFAULT = 1
STATE_COMMIT = 2 ## Informa a los hermanos que llegó un eof y le pide sus cantidades
STATE_OK = 3 ## Informa sus cantidades
STATE_CANCEL = 4 ## Informa que la operación no está lista aún

class EOFDTO(BatchDTO):
    def __init__(self, type, client:int, state:int, batch_id = 0, global_counter = 0, retry=0, query=0):
        self.operation_type = type
        self.state = state
        self.batch_id = batch_id
        self.retry = retry
        self.query = query
        super().__init__(client, global_counter)
    
    def is_ok(self):
        return self.state == STATE_OK
    
    def is_cancel(self):
        return self.state == STATE_CANCEL

    def is_commit(self):
        return self.state == STATE_COMMIT
    
    def is_EOF(self):
        return True
    
    def set_state(self, state):
        self.state = state

    def get_type(self):
        if self.operation_type == OperationType.OPERATION_TYPE_GAMES_EOF_DTO.value:
            return "games"
        return "reviews"
    
    def set_counter(self, counter):
        self.global_counter = counter
    
    def serialize(self):
        eof_bytes = bytearray()
        eof_bytes.extend(self.operation_type.to_bytes(1, byteorder='big'))
        eof_bytes.extend(self.client_id.to_bytes(1, byteorder='big'))
        eof_bytes.extend(self.global_counter.to_bytes(6, byteorder='big'))
        eof_bytes.extend(self.state.to_bytes(1, byteorder='big'))
        eof_bytes.extend(self.batch_id.to_bytes(2, byteorder='big'))
        eof_bytes.extend(self.retry.to_bytes(1, byteorder='big'))
        eof_bytes.extend(self.query.to_bytes(1, byteorder='big'))
        return bytes(eof_bytes)
    
    def deserialize(data, offset):
        offset -= 1
        operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        client = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        global_counter = int.from_bytes(data[offset:offset+6], byteorder='big')
        offset += 6
        state = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        batch_id = int.from_bytes(data[offset:offset+2], byteorder='big')
        offset += 2
        retry = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        query = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        return EOFDTO(operation_type, client, state, batch_id, global_counter, retry, query), offset