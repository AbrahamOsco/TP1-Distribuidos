class Structure:
    def __init__(self):
        pass

    def reset(self, client_id):
        pass

    def to_bytes(self):
        structure_bytes = bytearray()
        return bytes(structure_bytes)

    def from_bytes(self, data):
        return self, 0
    
    def print_state(self):
        pass
        