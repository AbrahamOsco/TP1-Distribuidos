from system.commonsSystem.DTO.GameStateDTO import GameStateDTO
from common.DTO.Query1ResultDTO import Query1ResultDTO

class PlatformDTO(GameStateDTO):
    def __init__(self, windows: int =0, mac: int = 0, linux: int = 0):
        self.windows = windows
        self.mac = mac
        self.linux = linux

    def get_platform_count(self):
        return {
            "windows": self.windows,
            "mac": self.mac,
            "linux": self.linux
        }
    
    def serialize(self):
        platform_bytes = bytearray()
        platform_bytes.extend(self.windows.to_bytes(4, byteorder='big'))
        platform_bytes.extend(self.mac.to_bytes(4, byteorder='big'))
        platform_bytes.extend(self.linux.to_bytes(4, byteorder='big'))
        return bytes(platform_bytes)

    def deserialize(data, offset):
        windows = int.from_bytes(data[offset:offset + 4], byteorder='big')
        offset += 4
        mac = int.from_bytes(data[offset:offset + 4], byteorder='big')
        offset += 4
        linux = int.from_bytes(data[offset:offset + 4], byteorder='big')
        offset += 4
        return PlatformDTO(windows=windows, mac=mac, linux=linux), offset
    
    def from_state(game):
        return PlatformDTO(windows=game.windows, mac=game.mac, linux=game.linux)
    
    def to_result(self):
        return Query1ResultDTO(self.windows, self.linux, self.mac)