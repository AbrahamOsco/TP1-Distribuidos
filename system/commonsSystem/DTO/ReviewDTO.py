from system.commonsSystem.DTO.enums.OperationType import OperationType
INITIAL_GAME = 1

class ReviewDTO:
    def __init__(self, status = INITIAL_GAME, app_id ="", client ="", review_text ="", review_score =""):
        self.operation_type = OperationType.OPERATION_TYPE_REVIEW
        self.status = status
        self.client = client
        self.app_id = int(app_id)
        self.review_text = review_text
        self.review_score = int(review_score)

    def to_string(self):
        return f"REVIEW|{self.app_id}|{self.client}|{self.review_text}|{self.review_score}"
    
    def from_string(data):
        data = data.split("|")
        return ReviewDTO(data[1], data[2], data[3], data[4])

    def is_EOF(self):
        return False
    
    def get_client(self):
        return self.client
    
    def retain(self, fields_to_keep):
        attributes = vars(self)
        for attr in list(attributes.keys()):
            if attr not in fields_to_keep:
                setattr(self, attr, None)
        return self