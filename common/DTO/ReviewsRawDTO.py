OPERATION_TYPE_REVIEWS_RAW = 40

class ReviewsRawDTO:
    def __init__(self, reviews_raw=[], batch_id=0):
        self.operation_type = OPERATION_TYPE_REVIEWS_RAW
        self.data_raw = reviews_raw
        self.batch_id = batch_id