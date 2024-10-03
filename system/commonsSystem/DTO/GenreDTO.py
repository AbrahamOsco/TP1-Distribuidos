from system.commonsSystem.DTO.GameStateDTO import GameStateDTO
from system.commonsSystem.DTO.DTO import DTO

class GenreDTO(GameStateDTO):
    def __init__(self, name: str ="", genres: str ="", release_date: str ="", avg_playtime_forever: int =0):
        self.name = name
        self.genres = genres
        self.release_date = release_date
        self.avg_playtime_forever = avg_playtime_forever

    def serialize(self):
        genre_bytes = bytearray()
        genre_bytes.extend(self.serialize_str(self.name))
        genre_bytes.extend(self.serialize_str(self.genres))
        genre_bytes.extend(self.serialize_str(self.release_date))
        genre_bytes.extend(self.avg_playtime_forever.to_bytes(4, byteorder='big'))
        return bytes(genre_bytes)

    def deserialize(data, offset):
        name, offset = DTO.deserialize_str(data, offset)
        genres, offset = DTO.deserialize_str(data, offset)
        release_date, offset = DTO.deserialize_str(data, offset)
        avg_playtime_forever = int.from_bytes(data[offset:offset+4], byteorder='big')
        offset += 4
        return GenreDTO(name=name, genres=genres, release_date=release_date, avg_playtime_forever=avg_playtime_forever), offset

    def from_state(game):
        return GenreDTO(name=game.name, genres=game.genres, release_date=game.release_date, avg_playtime_forever=game.avg_playtime_forever)