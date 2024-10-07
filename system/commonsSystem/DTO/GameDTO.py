import logging
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.utils.serialize import serialize_str, deserialize_str

STATE_GAMES_INITIAL = 1
STATE_PLATFORM = 2
STATE_GENRES = 3

class GameDTO:
    def __init__(self, app_id =0, name ="", windows =0,
            mac =0, linux =0, genres ="", release_date ="", avg_playtime_forever =0):
        self.operation_type = OperationType.OPERATION_TYPE_GAME
        self.app_id = app_id
        self.name = name
        self.release_date = release_date
        self.windows = int(windows)
        self.mac = int(mac)
        self.linux = int(linux)
        self.avg_playtime_forever = avg_playtime_forever
        self.genres = genres

    def serialize(self, state_games:int):
        game_bytes = bytearray()
        game_bytes.extend(self.operation_type.value.to_bytes(1, byteorder='big'))
        if state_games == STATE_PLATFORM:
            game_bytes.extend(self.windows.to_bytes(1, byteorder='big'))
            game_bytes.extend(self.mac.to_bytes(1, byteorder='big'))
            game_bytes.extend(self.linux.to_bytes(1, byteorder='big'))
            return game_bytes
        game_bytes.extend(self.app_id.to_bytes(8, byteorder='big'))
        game_bytes.extend(serialize_str(self.name))
        game_bytes.extend(serialize_str(self.release_date))
        game_bytes.extend(self.windows.to_bytes(1, byteorder='big'))
        game_bytes.extend(self.mac.to_bytes(1, byteorder='big'))
        game_bytes.extend(self.linux.to_bytes(1, byteorder='big'))
        game_bytes.extend(self.avg_playtime_forever.to_bytes(8, byteorder='big'))
        game_bytes.extend(serialize_str(self.genres))
        return game_bytes

    def deserialize(self, data, offset, state_games:int):
        operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        if state_games == STATE_PLATFORM:
            windows = int.from_bytes(data[offset:offset+1], byteorder='big')
            offset += 1
            mac = int.from_bytes(data[offset:offset+1], byteorder='big')
            offset += 1
            linux = int.from_bytes(data[offset:offset+1], byteorder='big')
            offset += 1
            return GameDTO(windows =windows, mac =mac, linux =linux), offset
        
        app_id = int.from_bytes(data[offset:offset+8], byteorder='big')
        offset += 8
        name, offset = deserialize_str(data, offset)
        release_date, offset = deserialize_str(data, offset)
        windows = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        mac = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        linux = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        avg_playtime_forever = int.from_bytes(data[offset:offset+8], byteorder='big')
        offset += 8
        genres, offset = deserialize_str(data, offset)
        return GameDTO(app_id =app_id, name =name, windows =windows,
                       mac =mac, linux =linux, genres =genres, release_date =release_date, 
                       avg_playtime_forever =avg_playtime_forever), offset
