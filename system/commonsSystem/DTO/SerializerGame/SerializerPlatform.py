from system.commonsSystem.utils.serialize import serialize_str, deserialize_str

class SerializerPlatform:
    def __init__(self):
        pass
    
    def serialize(self, game_dto):
        game_bytes = bytearray()
        game_bytes.extend(game_dto.operation_type.value.to_bytes(1, byteorder='big'))
        game_bytes.extend(game_dto.windows.to_bytes(1, byteorder='big'))
        game_bytes.extend(game_dto.mac.to_bytes(1, byteorder='big'))
        game_bytes.extend(game_dto.linux.to_bytes(1, byteorder='big'))
        return game_bytes

    def deserialize(self, data, offset):
        from system.commonsSystem.DTO.GameDTO import GameDTO
        operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        windows = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        mac = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        linux = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1

        return GameDTO(windows =windows, mac =mac, linux =linux), offset
