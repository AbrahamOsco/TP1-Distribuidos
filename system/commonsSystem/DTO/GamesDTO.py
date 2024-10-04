import logging
from system.commonsSystem.DTO.DTO import DTO
from system.commonsSystem.DTO.GameDTO import GameDTO
from system.commonsSystem.DTO.enums.OperationType import OperationType
STATE_GAMES_INITIAL = 1
STATE_PLATFORM = 2
STATE_Q2345 = 3
STATE_GENDER = 4
STATE_DECADE = 5
STATE_TOP_AVERAGE_PLAYTIME = 6

class GamesDTO(DTO):
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
            a_game_dto = GameDTO(app_id =int(game_raw[0]), name =game_raw[1],
                release_date =game_raw[2], windows =self.command_platform[game_raw[3]],
                mac =self.command_platform[game_raw[4]] , linux =self.command_platform[game_raw[5]],
                avg_playtime_forever =int(game_raw[6]), genres =game_raw[7])
            self.games_dto.append(a_game_dto)

    def serialize(self):
        games_bytes = bytearray()
        games_bytes.extend(self.operation_type.value.to_bytes(1, byteorder='big'))
        games_bytes.extend(self.client_id.to_bytes(1, byteorder='big'))
        games_bytes.extend(self.state_games.to_bytes(1, byteorder='big'))
        games_bytes.extend(len(self.games_dto).to_bytes(2, byteorder='big'))

        for game in self.games_dto:
            games_bytes.extend(game.serialize(self.state_games))
        return bytes(games_bytes)    

    def deserialize(self, data, offset):
        operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        client_id = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        state_games = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        games_dto_length = int.from_bytes(data[offset:offset+2], byteorder='big')
        offset += 2
        
        some_games_dto = []
        for i in range(games_dto_length):
            game, offset = GameDTO().deserialize(data, offset, state_games)
            some_games_dto.append(game)
        gamesDTO = GamesDTO(state_games =state_games, client_id =client_id, games_dto =some_games_dto)
        return gamesDTO, offset
