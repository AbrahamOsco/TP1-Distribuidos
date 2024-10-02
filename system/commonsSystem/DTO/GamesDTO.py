from system.commonsSystem.DTO.DTO import DTO
from system.commonsSystem.DTO.GameMinimalDTO import GameMinimalDTO
from system.commonsSystem.DTO.PlatformDTO import PlatformDTO
from system.commonsSystem.DTO.enums.OperationType import OperationType

STATE_GAMES_MINIMAL = 1
STATE_PLATFORM = 2

stateToClass = {
    STATE_GAMES_MINIMAL: GameMinimalDTO,
    STATE_PLATFORM: PlatformDTO,
}

class GamesDTO(DTO):
    def __init__(self, client_id:int=0, state_games:int=0, games_dto =[]):
        self.operation_type = OperationType.OPERATION_TYPE_GAMES_DTO
        self.client_id = client_id
        self.state_games = state_games 
        self.games_dto = games_dto

    def serialize(self):
        games_bytes = bytearray()
        games_bytes.extend(self.operation_type.value.to_bytes(1, byteorder='big'))
        games_bytes.extend(self.client_id.to_bytes(1, byteorder='big'))
        games_bytes.extend(self.state_games.to_bytes(1, byteorder='big'))
        games_bytes.extend(len(self.games_dto).to_bytes(2, byteorder='big'))
        for game in self.games_dto:
            games_bytes.extend(game.serialize())
        return bytes(games_bytes)

    def deserialize(data, offset):
        client_id = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        state_games = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        games_dto_length = int.from_bytes(data[offset:offset+2], byteorder='big')
        offset += 2
        
        some_games_dto = []
        for _ in range(games_dto_length):
            game, offset = stateToClass[state_games].deserialize(data, offset)
            some_games_dto.append(game)
        gamesDTO = GamesDTO(state_games=state_games, client_id=client_id, games_dto=some_games_dto)
        return gamesDTO, offset

    def set_state(self, state_games):
        self.state_games = state_games

    def from_raw(client_id, data_raw, indexes):
        games_dto = []
        for game_raw in data_raw:
            games_dto.append(GameMinimalDTO.from_raw(game_raw, indexes))
        return GamesDTO(client_id=client_id, games_dto=games_dto)