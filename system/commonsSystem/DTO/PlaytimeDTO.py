from system.commonsSystem.DTO.GameStateDTO import GameStateDTO
from system.commonsSystem.DTO.DTO import DTO

class PlaytimeDTO(GameStateDTO):
    def __init__(self, app_id="", name="", avg_playtime_forever:int=0):
        self.app_id = app_id
        self.name = name
        self.avg_playtime_forever = int(avg_playtime_forever)
    
    def serialize(self):
        platform_bytes = bytearray()
        platform_bytes.extend(DTO.serialize_str(self.app_id))
        platform_bytes.extend(DTO.serialize_str(self.name))
        platform_bytes.extend(self.avg_playtime_forever.to_bytes(4, byteorder='big'))
        return bytes(platform_bytes)

    def deserialize(data, offset):
        app_id, offset = DTO.deserialize_str(data, offset)
        name, offset = DTO.deserialize_str(data, offset)
        avg_playtime_forever = int.from_bytes(data[offset:offset+4], byteorder='big')
        offset += 4
        return PlaytimeDTO(app_id=app_id, name=name, avg_playtime_forever=avg_playtime_forever), offset
    
    def from_state(game):
        return PlaytimeDTO(app_id=game.app_id, name=game.name, avg_playtime_forever=int(game.avg_playtime_forever))