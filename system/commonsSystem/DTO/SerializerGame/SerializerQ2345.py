from system.commonsSystem.utils.serialize import serialize_str, deserialize_str

class SerializerQ2345:
    def __init__(self):
        pass

    def serialize(self, game_dto):
        game_bytes = bytearray()
        game_bytes.extend(game_dto.operation_type.value.to_bytes(1, byteorder='big'))

        game_bytes.extend(game_dto.app_id.to_bytes(8, byteorder='big'))
        game_bytes.extend(serialize_str(game_dto.name))

        game_bytes.extend(serialize_str(game_dto.release_date))
        game_bytes.extend(game_dto.avg_playtime_forever.to_bytes(8, byteorder='big'))
        game_bytes.extend(serialize_str(game_dto.genres))
        return game_bytes

    def deserialize(self, data, offset):
        from system.commonsSystem.DTO.GameDTO import GameDTO

        operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        app_id = int.from_bytes(data[offset:offset+8], byteorder='big')
        offset += 8
        name, offset = deserialize_str(data, offset)

        release_date, offset = deserialize_str(data, offset)
        avg_playtime_forever = int.from_bytes(data[offset:offset+8], byteorder='big')
        offset += 8
        genres, offset = deserialize_str(data, offset)

        return GameDTO(app_id =app_id, name =name, genres =genres, release_date =release_date, 
                       avg_playtime_forever =avg_playtime_forever), offset
