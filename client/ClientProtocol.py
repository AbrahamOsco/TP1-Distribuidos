from common.protocol.Protocol import Protocol

class ClientProtocol(Protocol):
    
    def __init__(self, socket):
        super().__init__(socket)  #uso super para invocar al constructor del padre. 

    def send_data_raw(self, games_raw):
        game_amount = len(games_raw)
        self.send_number_2_bytes(game_amount)
        for game in games_raw:
            element_amount = len(game)
            self.send_number_2_bytes(element_amount)
            for element in game:
                self.send_string(element)
        
                


            
