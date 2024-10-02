from system.commonsSystem.DTO.DTO import DTO

class GameStateDTO(DTO):
    def __init__(self):
        pass

    def get_platform_count(self):
        return {
            "windows": 0,
            "mac": 0,
            "linux": 0
        }
    
    def serialize(self):
        pass

    def deserialize(data, offset):
        pass