from system.commonsSystem.DTO.ReviewStateDTO import ReviewStateDTO
from system.commonsSystem.DTO.DTO import DTO

class ReviewIDNameDTO(ReviewStateDTO):
    def __init__(self, app_id:int=0, name=""):
        self.app_id = app_id
        self.name = name

    def serialize(self):
        review_bytes = bytearray()
        review_bytes.extend(self.app_id.to_bytes(4, byteorder='big'))
        review_bytes.extend(DTO.serialize_str(self.name))
        return bytes(review_bytes)

    def deserialize(data, offset):
        app_id = int.from_bytes(data[offset:offset+4], byteorder='big')
        offset += 4
        name, offset = DTO.deserialize_str(data, offset)
        return ReviewIDNameDTO(app_id=app_id, name=name), offset
    
    def from_state(review):
        return ReviewIDNameDTO(app_id=review.app_id,name=review.name)