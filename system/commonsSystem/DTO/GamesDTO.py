import logging
from system.commonsSystem.DTO.GameDTO import GameDTO
from system.commonsSystem.DTO.enums.OperationType import OperationType
STATE_GAMES_INITIAL = 1
STATE_PLATFORM = 2

class GamesDTO:
    def __init__(self, client_id:int, state_games:int,  games_raw =[], games_dto =[]):
        self.operation_type = OperationType.OPERATION_TYPE_GAMES_DTO
        self.client_id = client_id
        self.state_games = state_games 
        self.games_dto = games_dto
        self.command_platform = {"True":1, "False":0}
        if (games_raw != []):
            self.raw_to_dto(games_raw)
        
    def raw_to_dto(self, games_raw):
        self.games_dto = []
        for game_raw in games_raw:
            a_game_dto = GameDTO(app_id =game_raw[0], name =game_raw[1],
                release_date =game_raw[2], windows =self.command_platform[game_raw[3]],
                mac =self.command_platform[game_raw[4]] , linux =self.command_platform[game_raw[5]],
                avg_playtime_forever =game_raw[6], genres =game_raw[7])
            self.games_dto.append(a_game_dto)

    def set_state(self, state):
        self.state_games = state

    def get_client(self):
        return self.client_id

    def show_games_dto(self):
        logging.info(f"action: view status GamesDTO | operation_type: {self.operation_type} | client_id: {self.client_id}" +
                     f"| size_games_dto: {len(self.games_dto)} result: success ✅")
                     