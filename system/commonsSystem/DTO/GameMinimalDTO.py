from system.commonsSystem.DTO.GameStateDTO import GameStateDTO
from system.commonsSystem.DTO.DTO import DTO

indexMap = {
    "AppID": "app_id",
    "Name": "name",
    "Release date": "release_date",
    "Windows": "windows",
    "Mac": "mac",
    "Linux": "linux",
    "Average playtime forever": "avg_playtime_forever",
    "Genres": "genres"
}
command_platform = {"True":1, "False":0}

class GameMinimalDTO(GameStateDTO):
    def __init__(self, app_id="", name="", windows=0,
            mac=0, linux=0, genres="", release_date="", avg_playtime_forever=""):
        self.app_id = app_id
        self.name = name
        self.release_date = release_date
        self.windows = int(windows)
        self.mac = int(mac)
        self.linux = int(linux)
        self.avg_playtime_forever = avg_playtime_forever
        self.genres = genres

    def serialize(self):
        game_bytes = bytearray()
        game_bytes.extend(DTO.serialize_str(self.app_id))
        game_bytes.extend(DTO.serialize_str(self.name))
        game_bytes.extend(DTO.serialize_str(self.release_date))
        game_bytes.extend(self.windows.to_bytes(1, byteorder='big'))
        game_bytes.extend(self.mac.to_bytes(1, byteorder='big'))
        game_bytes.extend(self.linux.to_bytes(1, byteorder='big'))
        game_bytes.extend(DTO.serialize_str(self.avg_playtime_forever))
        game_bytes.extend(DTO.serialize_str(self.genres))
        return game_bytes

    def deserialize(data, offset):
        app_id, offset = DTO.deserialize_str(data, offset)
        name, offset = DTO.deserialize_str(data, offset)
        release_date, offset = DTO.deserialize_str(data, offset)
        windows = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        mac = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        linux = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        avg_playtime_forever, offset = DTO.deserialize_str(data, offset)
        genres, offset = DTO.deserialize_str(data, offset)
        return GameMinimalDTO(app_id=app_id, name=name, windows=windows,
                       mac=mac, linux=linux, genres=genres, release_date=release_date, 
                       avg_playtime_forever=avg_playtime_forever), offset

    def from_raw(data_raw, indexes):
        attributes = {}
        for i, value in enumerate(data_raw):
            if i in indexes.keys():
                if indexes[i] == "Windows" or indexes[i] == "Mac" or indexes[i] == "Linux":
                    attributes[indexMap[indexes[i]]] = command_platform[value]
                else:
                    attributes[indexMap[indexes[i]]] = value
        return GameMinimalDTO(app_id=attributes["app_id"], name=attributes["name"],
                              windows=attributes["windows"], mac=attributes["mac"], linux=attributes["linux"],
                              genres=attributes["genres"], release_date=attributes["release_date"],
                              avg_playtime_forever=attributes["avg_playtime_forever"])