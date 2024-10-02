import logging
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.DTO import DTO

STATE_PLATFORM = 2

class GameDTO(DTO):
    def __init__(self, app_id ="", name ="", windows =0,
            mac =0, linux =0, genres ="", release_date ="", avg_playtime_forever =""):
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
        # Preguntar segun el state games enviar q atributos y que no. 
        if state_games == STATE_PLATFORM:
            game_bytes.extend(self.windows.to_bytes(1, byteorder='big'))
            game_bytes.extend(self.mac.to_bytes(1, byteorder='big'))
            game_bytes.extend(self.linux.to_bytes(1, byteorder='big'))
            return game_bytes
        game_bytes.extend(self.serialize_str(self.app_id))
        game_bytes.extend(self.serialize_str(self.name))
        game_bytes.extend(self.serialize_str(self.release_date))
        game_bytes.extend(self.windows.to_bytes(1, byteorder='big'))
        game_bytes.extend(self.mac.to_bytes(1, byteorder='big'))
        game_bytes.extend(self.linux.to_bytes(1, byteorder='big'))
        game_bytes.extend(self.serialize_str(self.avg_playtime_forever))
        game_bytes.extend(self.serialize_str(self.genres))
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
        
        app_id, offset = self.deserialize_str(data, offset)
        name, offset = self.deserialize_str(data, offset)
        release_date, offset = self.deserialize_str(data, offset)
        windows = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        mac = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        linux = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        avg_playtime_forever, offset = self.deserialize_str(data, offset)
        genres, offset = self.deserialize_str(data, offset)
        return GameDTO(app_id =app_id, name =name, windows =windows,
                       mac =mac, linux =linux, genres =genres, release_date =release_date, 
                       avg_playtime_forever =avg_playtime_forever), offset


    #def show_game(self):
    #    logging.info(f"action: Show Game: {self.app_id}, {self.name}, {self.windows}, {self.mac}, {self.linux}, {self.genres}, {self.release_date}, {self.avg_playtime_forever}")
    #
    #def to_string(self):
    #    return f"GAME|;|{self.app_id}|;|{self.name}|;|{self.windows}|;|{self.mac}|;|{self.linux}|;|{self.genres}|;|{self.release_date}|;|{self.avg_playtime_forever}"
    #
    #def from_string(data):
    #    data = data.split("|;|")
    #    return GameDTO(data[1], data[3], data[4], data[5], data[6], data[7], data[8], data[9])
    #

    #def retain(self, fields_to_keep):
    #    attributes = vars(self)
    #    for attr in list(attributes.keys()):
    #        if attr not in fields_to_keep:
    #            setattr(self, attr, None)
    #    return self
