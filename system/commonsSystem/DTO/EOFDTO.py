STATE_DEFAULT = 1
STATE_COMMIT = 2
STATE_OK = 3
STATE_FINISH = 4

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
    
    def get_amount_received(self):
        return self.amount_received
    
    def get_amount_sent(self):
        return self.amount_sent
    
    def serialize(self):
        eof_bytes = bytearray()
        eof_bytes.extend(self.operation_type.value.to_bytes(1, byteorder='big'))
        eof_bytes.extend(self.client.to_bytes(1, byteorder='big'))
        eof_bytes.extend(self.state.to_bytes(1, byteorder='big'))
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
        amount_received = int.from_bytes(data[offset:offset+4], byteorder='big')
        offset += 4
        amount_sent = int.from_bytes(data[offset:offset+4], byteorder='big')
        offset += 4
        return EOFDTO(operation_type, client, state, amount_received, amount_sent), offset