from system.commonsSystem.DTO.DTO import DTO
from system.commonsSystem.DTO.GameStateDTO import GameStateDTO

class GameReviewedDTO(GameStateDTO):
    def __init__(self, app_id:int=0, name="", reviews:int=0):
        self.app_id = app_id
        self.name = name
        self.reviews = int(reviews)

    def serialize(self):
        reviewed_game_bytes = bytearray()
        reviewed_game_bytes.extend(self.app_id.to_bytes(4, byteorder='big'))
        reviewed_game_bytes.extend(DTO.serialize_str(self.name))
        reviewed_game_bytes.extend(self.reviews.to_bytes(4, byteorder='big'))
        return bytes(reviewed_game_bytes)
    
    def deserialize(data, offset):
        app_id = int.from_bytes(data[offset:offset+4], byteorder='big')
        offset += 4
        name, offset = DTO.deserialize_str(data, offset)
        reviews = int.from_bytes(data[offset:offset+4], byteorder='big')
        offset += 4
        return GameReviewedDTO(app_id=app_id, name=name, reviews=reviews), offset