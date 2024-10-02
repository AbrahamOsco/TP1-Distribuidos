from system.commonsSystem.DTO.enums.OperationType import OperationType

class ReviewedGameDTO:
    def __init__(self, app_id= "", reviews=""):
        self.operation_type = OperationType.OPERATION_TYPE_REVIEWED_GAME_DTO
        self.app_id = int(app_id)
        self.reviews = int(reviews)

    def serialize(self):
        reviewed_game_bytes = bytearray()
        reviewed_game_bytes.extend(self.operation_type.value.to_bytes(1, byteorder='big'))
        reviewed_game_bytes.extend(self.serialize_str(self.app_id))
        reviewed_game_bytes.extend(self.reviews.to_bytes(4, byteorder='big'))
        return bytes(reviewed_game_bytes)
    
    def deserialize(self, data, offset):
        offset += 1
        app_id, offset = self.deserialize_str(data, offset)
        reviews = int.from_bytes(data[offset:offset+4], byteorder='big')
        offset += 4
        return ReviewedGameDTO(app_id =app_id, reviews=reviews), offset
