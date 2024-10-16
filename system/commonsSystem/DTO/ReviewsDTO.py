import logging
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.ReviewDTO import ReviewDTO

STATE_REVIEW_INITIAL = 0

class ReviewsDTO:
    def __init__(self, client_id:int = 0, state_reviews:int = 0,  reviews_raw =[], reviews_dto =[]):
        self.operation_type = OperationType.OPERATION_TYPE_REVIEWS_DTO
        self.client_id = client_id
        self.state_reviews = state_reviews
        self.reviews_dto = reviews_dto
        if (reviews_raw != []):
            self.raw_to_dto(reviews_raw)
        
    def raw_to_dto(self, reviews_raw):
        self.reviews_dto = []
        for review_raw in reviews_raw:
            a_review_dto = ReviewDTO(app_id =int(review_raw[0]), review_text =review_raw[2], score= int(review_raw[3]))
            self.reviews_dto.append(a_review_dto)
    
    def serialize(self):
        reviews_bytes = bytearray()
        reviews_bytes.extend(self.operation_type.value.to_bytes(1, byteorder='big'))
        reviews_bytes.extend(self.client_id.to_bytes(1, byteorder='big'))
        reviews_bytes.extend(self.state_reviews.to_bytes(1, byteorder='big'))
        reviews_bytes.extend(len(self.reviews_dto).to_bytes(2, byteorder='big'))

        for review in self.reviews_dto:
            reviews_bytes.extend(review.serialize(self.state_reviews))
        return bytes(reviews_bytes)    

    def deserialize(self, data, offset):
        operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        client_id = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        state_reviews = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        review_dto_length = int.from_bytes(data[offset:offset+2], byteorder='big')
        offset += 2
        
        some_reviews_dto = []
        for i in range(review_dto_length):
            review, offset = ReviewDTO().deserialize(data, offset, state_reviews)
            some_reviews_dto.append(review)
        reviewsDTO = ReviewsDTO(client_id =client_id, reviews_dto =some_reviews_dto, state_reviews = state_reviews)
        return reviewsDTO