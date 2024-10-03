from system.commonsSystem.DTO.GameStateDTO import GameStateDTO
from system.commonsSystem.DTO.DTO import DTO

class GenreDTO(GameStateDTO):
    def __init__(self, app_id:int=0, name: str ="", release_date: str ="", avg_playtime_forever: int =0):
        self.app_id = int(app_id)
        self.name = name
        self.release_date = release_date
        self.avg_playtime_forever = int(avg_playtime_forever)

    def serialize(self):
        genre_bytes = bytearray()
        genre_bytes.extend(self.app_id.to_bytes(4, byteorder='big'))
        genre_bytes.extend(DTO.serialize_str(self.name))
        genre_bytes.extend(DTO.serialize_str(self.release_date))
        genre_bytes.extend(self.avg_playtime_forever.to_bytes(4, byteorder='big'))
        return bytes(genre_bytes)

    def deserialize(data, offset):
        app_id = int.from_bytes(data[offset:offset+4], byteorder='big')
        offset += 4
        name, offset = DTO.deserialize_str(data, offset)
        release_date, offset = DTO.deserialize_str(data, offset)
        avg_playtime_forever = int.from_bytes(data[offset:offset+4], byteorder='big')
        offset += 4
        return GenreDTO(app_id=app_id, name=name, release_date=release_date, avg_playtime_forever=avg_playtime_forever), offset

    def from_state(game):
        return GenreDTO(app_id=game.app_id, name=game.name, release_date=game.release_date, avg_playtime_forever=game.avg_playtime_forever)