from system.commonsSystem.DTO.enums.OperationType import OperationType

STATE_DEFAULT = 1
STATE_COMMIT = 2 ## Informa a los hermanos que llegó un eof y le pide sus cantidades
STATE_OK = 3 ## Informa sus cantidades
STATE_FINISH = 4 ## Informa que terminó y que el cliente debe ser eliminado de memoria

class EOFDTO:
    def __init__(self, type, client:int, state:int, batch_id = 0, global_counter = 0):
        self.operation_type = type
        self.state = state
        self.client = client
        self.batch_id = batch_id
        self.global_counter = global_counter
    
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
    
    def serialize(self):
        eof_bytes = bytearray()
        eof_bytes.extend(self.operation_type.to_bytes(1, byteorder='big'))
        eof_bytes.extend(self.client.to_bytes(1, byteorder='big'))
        eof_bytes.extend(self.global_counter.to_bytes(6, byteorder='big'))
        eof_bytes.extend(self.state.to_bytes(1, byteorder='big'))
        eof_bytes.extend(self.batch_id.to_bytes(2, byteorder='big'))
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
        return EOFDTO(operation_type, client, state, batch_id, global_counter), offset