OPERATION_TYPE_REVIEWS_INDEX_DTO = 38

class ReviewsIndexDTO:
    def __init__(self, client_id =0, reviews_raw = [], indexes = {}):
        self.operation_type = OPERATION_TYPE_REVIEWS_INDEX_DTO
        self.client_id = client_id
        self.indexes = indexes
        self.data_raw = reviews_raw
        


