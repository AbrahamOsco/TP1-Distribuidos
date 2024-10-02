OPERATION_TYPE_GAMES_RAW = 3

class GamesRawDTO:
    def __init__(self, client_id =0, games_raw=[]):
        self.operation_type = OPERATION_TYPE_GAMES_RAW
        self.client_id = client_id
        self.data_raw = games_raw
    
    
    
    