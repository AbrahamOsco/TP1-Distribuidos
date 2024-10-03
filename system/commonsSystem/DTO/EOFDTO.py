class EOFDTO:
    def __init__(self, type, client:int, confirmation=True):
        self.operation_type = type
        self.client = client
        self.confirmation = confirmation
    
    def is_confirmation(self):
        return self.confirmation
    
    def get_client(self):
        return self.client
    
    def is_EOF(self):
        return True
    
    def serialize(self):
        eof_bytes = bytearray()
        eof_bytes.extend(self.operation_type.value.to_bytes(1, byteorder='big'))
        eof_bytes.extend(self.client.to_bytes(1, byteorder='big'))
        eof_bytes.extend(self.confirmation.to_bytes(1, byteorder='big'))
        return bytes(eof_bytes)
    
    def deserialize(data, offset):
        offset -= 1
        operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        client = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        confirmation = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        return EOFDTO(operation_type, client, confirmation), offset