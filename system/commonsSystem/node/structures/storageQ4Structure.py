from system.commonsSystem.DTO.ReviewsDTO import STATE_IDNAME
from system.commonsSystem.node.structures.structure import Structure
import logging
import math

class StorageQ4Structure(Structure):
    def __init__(self, counter_size):
        self.incoming_state = STATE_IDNAME
        self.list = {}
        self.counter = {}
        self.counter_size = counter_size
        self.max_counter_size = 2 ** ((8 * counter_size) - 1) - 1

    def reset(self, client_id):
        if client_id not in self.list:
            return
        del self.list[client_id]
        del self.counter[client_id]

    def to_bytes(self):
        structure_bytes = bytearray()
        structure_bytes.extend(len(self.list).to_bytes(1, byteorder='big'))
        for key, value in self.list.items():
            structure_bytes.extend(key.to_bytes(1, byteorder='big'))
            structure_bytes.extend(len(value).to_bytes(4, byteorder='big'))
            for id, amount in value.items():
                structure_bytes.extend(id.to_bytes(4, byteorder='big'))
                structure_bytes.extend(amount.to_bytes(4, byteorder='big'))
            if (self.counter_size == 0):
                continue
            structure_bytes.extend(len(self.counter[key]).to_bytes(self.counter_size, byteorder='big'))
            for counter in self.counter[key]:
                structure_bytes.extend(counter.to_bytes(6, byteorder='big'))
        return bytes(structure_bytes)

    def add_counter(self, client_id, counter):
        self.counter[client_id].append(counter)
        if len(self.counter[client_id]) > self.max_counter_size:
            self.counter[client_id] = self.counter[client_id][math.ceil(self.max_counter_size*0.1):]
    
    def from_bytes(self, data):
        offset = 0
        if len(data) < offset + 1:
            return self, offset
        list_size = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        for i in range(list_size):
            client_id = int.from_bytes(data[offset:offset+1], byteorder='big')
            offset += 1
            game_size = int.from_bytes(data[offset:offset+4], byteorder='big')
            offset += 1
            self.list[client_id] = {}
            for j in range(game_size):
                app_id = int.from_bytes(data[offset:offset+4], byteorder='big')
                offset += 4
                amount = int.from_bytes(data[offset:offset+4], byteorder='big')
                offset += 4
                self.list[client_id][app_id] = amount
            counter_size = int.from_bytes(data[offset:offset+1], byteorder='big')
            offset += 1
            self.counter[client_id] = []
            for j in range(counter_size):
                counter = int.from_bytes(data[offset:offset+6], byteorder='big')
                offset += 6
                self.counter[client_id].append(counter)
        return self, offset
    
    def print_state(self):
        logging.info(f"List: {self.list}")
        logging.info(f"Counter: {self.counter}")
        