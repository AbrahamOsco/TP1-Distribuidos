from system.commonsSystem.DTO.GameStateDTO import GameStateDTO
from system.commonsSystem.DTO.DTO import DTO

class StateQ2345DTO(GameStateDTO):
    def __init__(self, app_id:int=0, name="", genres="", release_date="", avg_playtime_forever=""):
        self.app_id = int(app_id)
        self.name = name
        self.release_date = release_date
        self.avg_playtime_forever = avg_playtime_forever
        self.genres = genres
    
    def serialize(self):
        platform_bytes = bytearray()
        platform_bytes.extend(self.app_id.to_bytes(4, byteorder='big'))
        platform_bytes.extend(DTO.serialize_str(self.name))
        platform_bytes.extend(DTO.serialize_str(self.release_date))
        platform_bytes.extend(DTO.serialize_str(self.avg_playtime_forever))
        platform_bytes.extend(DTO.serialize_str(self.genres))
        return bytes(platform_bytes)

    def deserialize(data, offset):
        app_id = int.from_bytes(data[offset:offset+4], byteorder='big')
        offset += 4
        name, offset = DTO.deserialize_str(data, offset)
        release_date, offset = DTO.deserialize_str(data, offset)
        avg_playtime_forever, offset = DTO.deserialize_str(data, offset)
        genres, offset = DTO.deserialize_str(data, offset)
        return StateQ2345DTO(app_id=app_id, name=name, release_date=release_date, avg_playtime_forever=avg_playtime_forever, genres=genres), offset
    
    def from_state(game):
        return StateQ2345DTO(app_id=game.app_id, name=game.name, release_date=game.release_date, avg_playtime_forever=game.avg_playtime_forever, genres=game.genres)