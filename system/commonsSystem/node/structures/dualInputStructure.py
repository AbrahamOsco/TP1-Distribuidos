from system.commonsSystem.DTO.ReviewsDTO import STATE_TEXT, ReviewsDTO
from system.commonsSystem.DTO.DTO import DTO
from system.commonsSystem.node.structures.structure import Structure
import math
import logging

STATUS_STARTED = 0
STATUS_REVIEWING = 1

class DualInputStructure(Structure):
    def __init__(self, counter_size):
        self.incoming_state = STATE_TEXT
        self.list = {}
        self.games = {}
        self.status = {}
        self.premature_messages = {}
        self.counter = {}
        self.counter_size = counter_size
        self.max_counter_size = 2 ** ((8 * counter_size) - 1) - 1

    def reset(self, client_id):
        if client_id not in self.list:
            return
        del self.list[client_id]
        del self.games[client_id]
        del self.status[client_id]
        del self.counter[client_id]
        del self.premature_messages[client_id]

    def init(self, client_id):
        if client_id not in self.list:
            self.list[client_id] = {}
            self.games[client_id] = {}
            self.status[client_id] = STATUS_STARTED
            self.counter[client_id] = []
            self.premature_messages[client_id] = []

    def to_bytes(self):
        structure_bytes = bytearray()
        structure_bytes.extend(len(self.list).to_bytes(1, byteorder='big'))
        for key, value in self.list.items():
            structure_bytes.extend(key.to_bytes(1, byteorder='big'))
            structure_bytes.extend(self.status[key].to_bytes(1, byteorder='big'))
            structure_bytes.extend(len(value).to_bytes(4, byteorder='big'))
            for id, amount in value.items():
                structure_bytes.extend(id.to_bytes(4, byteorder='big'))
                structure_bytes.extend(amount.to_bytes(4, byteorder='big'))
                structure_bytes.extend(DTO.serialize_str(self.games[key][id]))
            structure_bytes.extend(len(self.premature_messages[key]).to_bytes(2, byteorder='big'))
            for message in self.premature_messages[key]:
                structure_bytes.extend(message.serialize())
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
            self.status[client_id] = int.from_bytes(data[offset:offset+1], byteorder='big')
            offset += 1
            game_size = int.from_bytes(data[offset:offset+4], byteorder='big')
            offset += 4
            self.list[client_id] = {}
            self.games[client_id] = {}
            for j in range(game_size):
                app_id = int.from_bytes(data[offset:offset+4], byteorder='big')
                offset += 4
                amount = int.from_bytes(data[offset:offset+4], byteorder='big')
                offset += 4
                game, offset = DTO.deserialize_str(data, offset)
                self.list[client_id][app_id] = amount
                self.games[client_id][app_id] = game
            premature_size = int.from_bytes(data[offset:offset+2], byteorder='big')
            offset += 2
            self.premature_messages[client_id] = []
            for j in range(premature_size):
                offset += 1
                message, offset = ReviewsDTO.deserialize(data, offset)
                self.premature_messages[client_id].append(message)
            self.counter[client_id] = []
            if (self.counter_size == 0):
                continue
            counter_len = int.from_bytes(data[offset:offset+self.counter_size], byteorder='big')
            offset += self.counter_size
            for j in range(counter_len):
                counter = int.from_bytes(data[offset:offset+6], byteorder='big')
                offset += 6
                self.counter[client_id].append(counter)
        return self, offset
    
    def print_state(self):
        logging.debug(f"List: {self.list}")
        logging.debug(f"Games: {self.games}")
        logging.debug(f"Status: {self.status}")
        logging.debug(f"Counter: {self.counter}")
        logging.debug(f"Premature messages: {self.premature_messages}")
        