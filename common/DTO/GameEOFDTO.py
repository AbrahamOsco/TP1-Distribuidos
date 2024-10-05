OPERATION_TYPE_GAMEEOF = 30

class GameEOFDTO:
    def __init__(self, client_id =0):
        self.operation_type = OPERATION_TYPE_GAMEEOF
        self.client_id = client_id
    
    
    
    