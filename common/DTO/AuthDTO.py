OPERATION_TYPE_AUTH = 10

class AuthDTO:
    def __init__(self, client_id =0):
        self.operation_type = OPERATION_TYPE_AUTH
        self.client_id = client_id
    
    
    
    