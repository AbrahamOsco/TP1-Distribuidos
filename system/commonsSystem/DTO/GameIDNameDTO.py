from system.commonsSystem.DTO.GameStateDTO import GameStateDTO
from system.commonsSystem.DTO.DTO import DTO

class GameIDNameDTO(GameStateDTO):
    def __init__(self, app_id:int=0, name: str =""):
        self.app_id = int(app_id)
        self.name = name

    def serialize(self):
        genre_bytes = bytearray()
        genre_bytes.extend(self.app_id.to_bytes(4, byteorder='big'))
        genre_bytes.extend(DTO.serialize_str(self.name))
        return bytes(genre_bytes)

    def deserialize(data, offset):
        app_id = int.from_bytes(data[offset:offset+4], byteorder='big')
        offset += 4
        name, offset = DTO.deserialize_str(data, offset)
        return GameIDNameDTO(app_id=app_id, name=name), offset

    def from_state(game):
        return GameIDNameDTO(app_id=game.app_id, name=game.name)