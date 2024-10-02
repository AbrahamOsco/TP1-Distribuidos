OPERATION_TYPE_REVIEWS_RAW = 40

class ReviewsRawDTO:
    def __init__(self, client_id =0, reviews_raw=[]):
        self.operation_type = OPERATION_TYPE_REVIEWS_RAW
        self.client_id = client_id
        self.data_raw = reviews_raw
