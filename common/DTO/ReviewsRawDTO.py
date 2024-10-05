OPERATION_TYPE_REVIEWS_RAW = 40

class ReviewsRawDTO:
    def __init__(self, reviews_raw=[]):
        self.operation_type = OPERATION_TYPE_REVIEWS_RAW
        self.data_raw = reviews_raw
