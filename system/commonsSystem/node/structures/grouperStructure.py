from system.commonsSystem.DTO.GamesDTO import STATE_PLAYTIME, STATE_REVIEWED
from system.commonsSystem.DTO.PlaytimeDTO import PlaytimeDTO
from system.commonsSystem.DTO.GameReviewedDTO import GameReviewedDTO
import logging

IncomingToClass = {
    STATE_PLAYTIME: PlaytimeDTO,
    STATE_REVIEWED: GameReviewedDTO
}

class GrouperStructure:
    def __init__(self, incoming_state):
        self.incoming_state = incoming_state
        self.list = {}
        self.min_time = {}
        self.counters = {}

    def reset(self, client_id):
        if client_id not in self.list:
            return
        del self.list[client_id]
        del self.min_time[client_id]
        del self.counters[client_id]

    def to_bytes(self):
        structure_bytes = bytearray()
        structure_bytes.extend(len(self.list).to_bytes(1, byteorder='big'))
        for key, value in self.list.items():
            structure_bytes.extend(key.to_bytes(1, byteorder='big'))
            structure_bytes.extend(len(value).to_bytes(1, byteorder='big'))
            for game in value:
                structure_bytes.extend(game.serialize())
            structure_bytes.extend(self.min_time[key].to_bytes(6, byteorder='big'))
            structure_bytes.extend(self.counters[key].to_bytes(6, byteorder='big'))
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
            game_size = int.from_bytes(data[offset:offset+1], byteorder='big')
            offset += 1
            self.list[client_id] = []
            for j in range(game_size):
                game, offset = IncomingToClass[self.incoming_state].deserialize(data, offset)
                self.list[client_id].append(game)
            self.min_time[client_id] = int.from_bytes(data[offset:offset+6], byteorder='big')
            offset += 6
            self.counters[client_id] = int.from_bytes(data[offset:offset+6], byteorder='big')
            offset += 6
        return self, offset
    
    def print_state(self):
        logging.info(f"List: {self.list}")
        logging.info(f"Min time: {self.min_time}")
        logging.info(f"Counters: {self.counters}")