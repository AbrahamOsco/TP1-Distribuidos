import logging
from system.commonsSystem.node.structures.structure import Structure

class PlatformStructure(Structure):
    def __init__(self):
        self.result = {}

    def reset(self, client_id):
        if client_id not in self.result:
            return
        del self.result[client_id]

    def to_bytes(self):
        structure_bytes = bytearray()
        structure_bytes.extend(len(self.result).to_bytes(1, byteorder='big'))
        for key, value in self.result.items():
            structure_bytes.extend(key.to_bytes(1, byteorder='big'))
            structure_bytes.extend(value["windows"].to_bytes(4, byteorder='big'))
            structure_bytes.extend(value["linux"].to_bytes(4, byteorder='big'))
            structure_bytes.extend(value["mac"].to_bytes(4, byteorder='big'))
            structure_bytes.extend(value["counter"].to_bytes(6, byteorder='big'))
        return bytes(structure_bytes)
    
    def from_bytes(self, data):
        offset = 0
        if len(data) < offset + 1:
            return self, offset
        list_size = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        for i in range(list_size):
            client_id = int.from_bytes(data[offset:offset+1], byteorder='big')
            offset += 1
            windows = int.from_bytes(data[offset:offset+4], byteorder='big')
            offset += 4
            linux = int.from_bytes(data[offset:offset+4], byteorder='big')
            offset += 4
            mac = int.from_bytes(data[offset:offset+4], byteorder='big')
            offset += 4
            counter = int.from_bytes(data[offset:offset+6], byteorder='big')
            offset += 6
            self.result[client_id] = {"windows": windows, "linux": linux, "mac": mac, "counter": counter}
        return self, offset
    
    def print_state(self):
        logging.info(f"Result: {self.result}")