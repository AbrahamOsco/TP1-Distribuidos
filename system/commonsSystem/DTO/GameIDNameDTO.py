from system.commonsSystem.DTO.GameStateDTO import GameStateDTO
from system.commonsSystem.DTO.DTO import DTO

class GameIDNameDTO(GameStateDTO):
    def __init__(self, app_id: str="", name: str =""):
        self.app_id = app_id
        self.name = name

    def serialize(self):
        genre_bytes = bytearray()
        genre_bytes.extend(DTO.serialize_str(self.app_id))
        genre_bytes.extend(DTO.serialize_str(self.name))
        return bytes(genre_bytes)

    def deserialize(data, offset):
        app_id, offset = DTO.deserialize_str(data, offset)
        name, offset = DTO.deserialize_str(data, offset)
        return GameIDNameDTO(app_id=app_id, name=name), offset

    def from_state(game):
        return GameIDNameDTO(app_id=game.app_id, name=game.name)