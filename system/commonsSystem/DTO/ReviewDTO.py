from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.utils.serialize import serialize_str, deserialize_str


class ReviewDTO:
    def __init__(self, app_id =0, review_text ="", score =0):
        self.operation_type = OperationType.OPERATION_TYPE_REVIEW
        self.app_id = app_id
        self.review_text = review_text
        self.score = score

    def serialize(self, state_games:int = 0):
        # Por ahora ignoraremos state_games we sent all fields. 
        review_bytes = bytearray()
        review_bytes.extend(self.operation_type.value.to_bytes(1, byteorder ='big'))
        review_bytes.extend(self.app_id.to_bytes(8, byteorder ='big'))
        review_bytes.extend(serialize_str(self.review_text))
        review_bytes.extend(self.score.to_bytes(1, byteorder ='big', signed =True))
        return review_bytes

    def deserialize(self, data, offset, state_games:int = 0):
        operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        app_id = int.from_bytes(data[offset:offset+8], byteorder='big')
        offset += 8
        review_text, offset = deserialize_str(data, offset)
        score = int.from_bytes(data[offset:offset+1], byteorder='big', signed =True)
        offset +=1
        return ReviewDTO(app_id, review_text, score), offset
