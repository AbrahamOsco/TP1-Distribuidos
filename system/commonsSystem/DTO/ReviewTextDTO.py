from system.commonsSystem.DTO.ReviewStateDTO import ReviewStateDTO
from system.commonsSystem.DTO.DTO import DTO

class ReviewTextDTO(ReviewStateDTO):
    def __init__(self, app_id:int=0, name:str="", review_text=""):
        self.app_id = int(app_id)
        self.name = name
        self.review_text = review_text

    def serialize(self):
        review_bytes = bytearray()
        review_bytes.extend(self.app_id.to_bytes(4, byteorder='big'))
        review_bytes.extend(DTO.serialize_str(self.name))
        review_bytes.extend(DTO.serialize_str(self.review_text))
        return bytes(review_bytes)

    def deserialize(data, offset):
        app_id = int.from_bytes(data[offset:offset+4], byteorder='big')
        offset += 4
        name, offset = DTO.deserialize_str(data, offset)
        review_text, offset = DTO.deserialize_str(data, offset)
        return ReviewTextDTO(app_id=app_id, name=name, review_text=review_text), offset

    def from_raw(data_raw, indexes):
        attributes = {}
        for i, value in enumerate(data_raw):
            if i in indexes.keys():
                attributes[indexes[i]] = value
        return ReviewTextDTO(app_id=attributes["app_id"], review_text=attributes["review_text"])
    
    def set_name(self, name):
        self.name = name

    def from_state(review):
        return ReviewTextDTO(app_id=review.app_id, review_text=review.review_text)