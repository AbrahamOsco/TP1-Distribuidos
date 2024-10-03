from system.commonsSystem.DTO.ReviewStateDTO import ReviewStateDTO
from system.commonsSystem.DTO.DTO import DTO

class ReviewMinimalDTO(ReviewStateDTO):
    def __init__(self, app_id="", review_text="", review_score=0):
        self.app_id = app_id
        self.review_text = review_text
        self.review_score = int(review_score)

    def serialize(self):
        review_bytes = bytearray()
        review_bytes.extend(self.app_id.to_bytes(4, byteorder='big'))
        review_bytes.extend(DTO.serialize_str(self.review_text))
        review_bytes.extend(self.review_score.to_bytes(1, byteorder='big'))
        return bytes(review_bytes)

    def deserialize(data, offset):
        app_id = int.from_bytes(data[offset:offset+4], byteorder='big')
        offset += 4
        review_text, offset = DTO.deserialize_str(data, offset)
        review_score = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        return ReviewMinimalDTO(app_id=app_id, review_text=review_text, review_score=review_score), offset

    def from_raw(data_raw, indexes):
        attributes = {}
        for i, value in enumerate(data_raw):
            if i in indexes.keys():
                attributes[indexes[i]] = value
        return ReviewMinimalDTO(app_id=attributes["app_id"], review_text=attributes["review_text"], review_score=attributes["review_score"])