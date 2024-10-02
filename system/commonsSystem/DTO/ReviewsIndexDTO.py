from system.commonsSystem.DTO.enums.OperationType import OperationType

class ReviewsIndexDTO:
    def __init__(self, client_id =0, reviews_raw = [], indexes = {}):
        self.operation_type = OperationType.OPERATION_TYPE_REVIEWS_INDEX_DTO
        self.client_id = client_id
        self.indexes = indexes
        self.data_raw = reviews_raw

    def get_client(self):
        return self.client_id
        


