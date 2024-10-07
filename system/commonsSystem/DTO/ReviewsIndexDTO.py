from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.IndexDTO import IndexDTO

class ReviewsIndexDTO(IndexDTO):
    def __init__(self, client_id =0, reviews_raw = [], indexes = {}):
        super().__init__(client_id =client_id, data_raw =reviews_raw, indexes =indexes)
        self.operation_type = OperationType.OPERATION_TYPE_REVIEWS_INDEX_DTO

    def get_client(self):
        return self.client_id
        
    def get_instance(self, client_id, indexes, items_raw, offset):
        return ReviewsIndexDTO(client_id =client_id, indexes =indexes, reviews_raw =items_raw)
