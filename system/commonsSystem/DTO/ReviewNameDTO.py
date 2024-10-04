from system.commonsSystem.DTO.ReviewStateDTO import ReviewStateDTO
from system.commonsSystem.DTO.DTO import DTO

class ReviewNameDTO(ReviewStateDTO):
    def __init__(self, name=""):
        self.name = name

    def serialize(self):
        review_bytes = bytearray()
        review_bytes.extend(DTO.serialize_str(self.name))
        return bytes(review_bytes)

    def deserialize(data, offset):
        name, offset = DTO.deserialize_str(data, offset)
        return ReviewNameDTO(name=name), offset
    
    def from_state(review):
        return ReviewNameDTO(name=review.name)