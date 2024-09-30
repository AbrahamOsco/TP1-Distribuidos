import logging
from system.commonsSystem.DTO.GameDTO import GameDTO
OPERATION_TYPE_GAMES_DTO = 2
STATE_GAMES_INITIAL = 1

class GamesDTO:
    def __init__(self, client_id:int, state_games:int,  games_raw =[], games_dto =[]):
        self.operation_type = OPERATION_TYPE_GAMES_DTO
        self.client_id = client_id
        self.state_games = state_games 
        self.games_dto = games_dto
        self.command_platform = {"True":1, "False":0}
        if (games_raw != []): 
            self.map_to_dto(games_raw)
        
    def map_to_dto(self, games_raw):
        self.games_dto = []
        for game_raw in games_raw:
            a_game_dto = GameDTO(app_id =game_raw[0], client_id =self.client_id, name =game_raw[1], \
                release_date =game_raw[2], windows =self.command_platform[game_raw[3]], \
                mac =self.command_platform[game_raw[4]] , linux =self.command_platform[game_raw[5]], \
                avg_playtime_forever =game_raw[6], genres =game_raw[7])
            self.games_dto.append(a_game_dto)

    def show_games_dto(self):
        logging.info(f"operation_type: {self.operation_type} | client_id: {self.client_id} | size_games_dto: {len(self.games_dto)}")

    
"""    # Recibiremos batch de games de a lo sumo 65535 games (2 bytes)
    def to_bytes(self):
        operation_type_bytes = (self.operation_type).to_bytes(1, byteorder='big')
        client_id_bytes = (self.client_id).to_bytes(1, byteorder='big')
        size_games_bytes = (len(self.games_dto)).to_bytes(2, byteorder='big')
        for a_game in self.games_dto:
            pass"""