OPERATION_TYPE_GAMES_RAW = 50

class GamesRawDTO:
    def __init__(self, games_raw=[]):
        self.operation_type = OPERATION_TYPE_GAMES_RAW
        self.data_raw = games_raw
    
    
    
    