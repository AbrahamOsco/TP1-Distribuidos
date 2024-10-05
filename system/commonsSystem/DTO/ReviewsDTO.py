from system.commonsSystem.DTO.DTO import DTO
from system.commonsSystem.DTO.ReviewMinimalDTO import ReviewMinimalDTO
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.ReviewStateDTO import ReviewStateDTO
from system.commonsSystem.DTO.ReviewTextDTO import ReviewTextDTO
from system.commonsSystem.DTO.ReviewNameDTO import ReviewNameDTO

STATE_REVIEW_MINIMAL = 1
STATE_TEXT = 2
STATE_NAME = 3

stateToClass = {
    STATE_REVIEW_MINIMAL: ReviewMinimalDTO,
    STATE_TEXT: ReviewTextDTO,
    STATE_NAME: ReviewNameDTO,
}

class ReviewsDTO(DTO):
    def __init__(self, client_id:int=0, state_reviews:int=0, reviews_dto: list[ReviewStateDTO] =[]):
        self.operation_type = OperationType.OPERATION_TYPE_REVIEWS_DTO
        self.client_id = client_id
        self.state_reviews = state_reviews
        self.reviews_dto = reviews_dto

    def serialize(self):
        reviews_bytes = bytearray()
        reviews_bytes.extend(self.operation_type.value.to_bytes(1, byteorder='big'))
        reviews_bytes.extend(self.client_id.to_bytes(1, byteorder='big'))
        reviews_bytes.extend(self.state_reviews.to_bytes(1, byteorder='big'))
        reviews_bytes.extend(len(self.reviews_dto).to_bytes(2, byteorder='big'))
        for game in self.reviews_dto:
            reviews_bytes.extend(game.serialize())
        return bytes(reviews_bytes)

    def deserialize(data, offset):
        client_id = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        state_reviews = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        reviews_dto_length = int.from_bytes(data[offset:offset+2], byteorder='big')
        offset += 2
        
        some_reviews_dto = []
        for _ in range(reviews_dto_length):
            game, offset = stateToClass[state_reviews].deserialize(data, offset)
            some_reviews_dto.append(game)
        reviewsDTO = ReviewsDTO(client_id=client_id, state_reviews=state_reviews, reviews_dto=some_reviews_dto)
        return reviewsDTO, offset

    def set_state(self, state_reviews):
        self.state_reviews = state_reviews
        self.reviews_dto = list(map(lambda game: stateToClass[state_reviews].from_state(game), self.reviews_dto))

    def is_EOF(self):
        return False
    
    def is_reviews(self):
        return True
    
    def is_games(self):
        return False
    
    def get_amount_of_reviews(self):
        return len(self.reviews_dto)
    
    def get_client(self):
        return self.client_id

    def filter_reviews(self, filter_func):
        self.reviews_dto = list(filter(filter_func, self.reviews_dto))

    def apply_on_reviews(self, func):
        for review in self.reviews_dto:
            func(review)

    def from_raw(client_id: int, data_raw:str, indexes):
        reviews_dto = []
        for game_raw in data_raw:
            reviews_dto.append(ReviewMinimalDTO.from_raw(game_raw, indexes))
        return ReviewsDTO(client_id=client_id, state_reviews=STATE_REVIEW_MINIMAL, reviews_dto=reviews_dto)