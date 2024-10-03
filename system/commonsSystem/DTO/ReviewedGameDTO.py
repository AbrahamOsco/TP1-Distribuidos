from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.DTO import DTO

class ReviewedGameDTO:
    def __init__(self, client_id:int=0, name="", reviews=""):
        self.operation_type = OperationType.OPERATION_TYPE_REVIEWED_GAME_DTO
        self.client_id = client_id
        self.name = name
        self.reviews = int(reviews)

    def serialize(self):
        reviewed_game_bytes = bytearray()
        reviewed_game_bytes.extend(self.operation_type.value.to_bytes(1, byteorder='big'))
        reviewed_game_bytes.extend(self.client_id.to_bytes(1, byteorder='big'))
        reviewed_game_bytes.extend(DTO.serialize_str(self.name))
        reviewed_game_bytes.extend(self.reviews.to_bytes(4, byteorder='big'))
        return bytes(reviewed_game_bytes)
    
    def deserialize(data, offset):
        client_id = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        name, offset = DTO.deserialize_str(data, offset)
        reviews = int.from_bytes(data[offset:offset+4], byteorder='big')
        offset += 4
        return ReviewedGameDTO(name=name, reviews=reviews), offset

    def is_EOF(self):
        return False
    
    def get_client(self):
        return self.client_id