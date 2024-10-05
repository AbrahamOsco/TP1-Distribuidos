OPERATION_TYPE_REVIEWEOF = 35

class ReviewsEOFDTO:
    def __init__(self, client_id =0):
        self.operation_type = OPERATION_TYPE_REVIEWEOF
        self.client_id = client_id
    
    
    
    