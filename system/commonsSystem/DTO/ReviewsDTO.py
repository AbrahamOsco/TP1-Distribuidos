from system.commonsSystem.DTO.BatchDTO import BatchDTO
from system.commonsSystem.DTO.ReviewMinimalDTO import ReviewMinimalDTO
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.ReviewStateDTO import ReviewStateDTO
from system.commonsSystem.DTO.ReviewTextDTO import ReviewTextDTO
from system.commonsSystem.DTO.ReviewIDNameDTO import ReviewIDNameDTO
from system.commonsSystem.DTO.RawDTO import RawDTO

STATE_REVIEW_MINIMAL = 1
STATE_TEXT = 2
STATE_IDNAME = 3

stateToClass = {
    STATE_REVIEW_MINIMAL: ReviewMinimalDTO,
    STATE_TEXT: ReviewTextDTO,
    STATE_IDNAME: ReviewIDNameDTO,
}

class ReviewsDTO(BatchDTO):
    def __init__(self, client_id:int=0, state_reviews:int=0, reviews_dto: list[ReviewStateDTO] =[], global_counter=0):
        self.operation_type = OperationType.OPERATION_TYPE_REVIEWS_DTO
        self.client_id = client_id
        self.state_reviews = state_reviews
        self.reviews_dto = reviews_dto
        self.global_counter = global_counter

    def serialize(self):
        reviews_bytes = bytearray()
        reviews_bytes.extend(self.operation_type.value.to_bytes(1, byteorder='big'))
        reviews_bytes.extend(self.client_id.to_bytes(1, byteorder='big'))
        reviews_bytes.extend(self.global_counter.to_bytes(6, byteorder='big'))
        reviews_bytes.extend(self.state_reviews.to_bytes(1, byteorder='big'))
        reviews_bytes.extend(len(self.reviews_dto).to_bytes(2, byteorder='big'))
        for game in self.reviews_dto:
            reviews_bytes.extend(game.serialize())
        return bytes(reviews_bytes)

    def deserialize(data, offset):
        client_id = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        global_counter = int.from_bytes(data[offset:offset+6], byteorder='big')
        offset += 6
        state_reviews = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        reviews_dto_length = int.from_bytes(data[offset:offset+2], byteorder='big')
        offset += 2
        
        some_reviews_dto = []
        for _ in range(reviews_dto_length):
            game, offset = stateToClass[state_reviews].deserialize(data, offset)
            some_reviews_dto.append(game)
        reviewsDTO = ReviewsDTO(client_id=client_id, state_reviews=state_reviews, reviews_dto=some_reviews_dto, global_counter=global_counter)
        return reviewsDTO, offset

    def get_amount(self):
        return len(self.reviews_dto)

    def set_state(self, state_reviews):
        self.state_reviews = state_reviews
        self.reviews_dto = list(map(lambda game: stateToClass[state_reviews].from_state(game), self.reviews_dto))
    
    def is_reviews(self):
        return True

    def filter_data(self, filter_func):
        self.reviews_dto = list(filter(filter_func, self.reviews_dto))

    def apply_on_reviews(self, func):
        for review in self.reviews_dto:
            func(review)

    def from_raw(raw_dto: RawDTO, indexes):
        reviews_dto = []
        for review_raw in raw_dto.raw_data:
            review = ReviewMinimalDTO.from_raw(review_raw, indexes)
            if review is None:
                continue
            reviews_dto.append(review)
        return ReviewsDTO(client_id=raw_dto.client_id, state_reviews=STATE_REVIEW_MINIMAL, reviews_dto=reviews_dto, global_counter=raw_dto.global_counter)