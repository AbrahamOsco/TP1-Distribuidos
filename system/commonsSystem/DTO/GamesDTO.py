from system.commonsSystem.DTO.DTO import DTO
from system.commonsSystem.DTO.GameMinimalDTO import GameMinimalDTO
from system.commonsSystem.DTO.PlatformDTO import PlatformDTO
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.GameStateDTO import GameStateDTO
from system.commonsSystem.DTO.StateQ2345DTO import StateQ2345DTO
from system.commonsSystem.DTO.GenreDTO import GenreDTO
from system.commonsSystem.DTO.PlaytimeDTO import PlaytimeDTO
from system.commonsSystem.DTO.GameIDNameDTO import GameIDNameDTO
from system.commonsSystem.DTO.RawDTO import RawDTO
from system.commonsSystem.DTO.GameReviewedDTO import GameReviewedDTO
from common.DTO.Query2345ResultDTO import Query2345ResultDTO

STATE_GAMES_MINIMAL = 1
STATE_PLATFORM = 2
STATE_Q2345 = 3
STATE_GENRE = 4
STATE_PLAYTIME = 5
STATE_IDNAME = 6
STATE_REVIEWED = 7

stateToClass = {
    STATE_GAMES_MINIMAL: GameMinimalDTO,
    STATE_PLATFORM: PlatformDTO,
    STATE_Q2345: StateQ2345DTO,
    STATE_GENRE: GenreDTO,
    STATE_PLAYTIME: PlaytimeDTO,
    STATE_IDNAME: GameIDNameDTO,
    STATE_REVIEWED: GameReviewedDTO
}

class GamesDTO(DTO):
    def __init__(self, client_id:int=0, state_games:int=0, games_dto: list[GameStateDTO] =[], query:int=0):
        self.operation_type = OperationType.OPERATION_TYPE_GAMES_DTO
        self.client_id = client_id
        self.state_games = state_games 
        self.games_dto = games_dto
        self.query = 0

    def serialize(self):
        games_bytes = bytearray()
        games_bytes.extend(self.operation_type.value.to_bytes(1, byteorder='big'))
        games_bytes.extend(self.client_id.to_bytes(1, byteorder='big'))
        games_bytes.extend(self.state_games.to_bytes(1, byteorder='big'))
        games_bytes.extend(self.query.to_bytes(1, byteorder='big'))
        games_bytes.extend(len(self.games_dto).to_bytes(2, byteorder='big'))
        for game in self.games_dto:
            games_bytes.extend(game.serialize())
        return bytes(games_bytes)

    def deserialize(data, offset):
        client_id = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        state_games = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        query = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        games_dto_length = int.from_bytes(data[offset:offset+2], byteorder='big')
        offset += 2
        
        some_games_dto = []
        for _ in range(games_dto_length):
            game, offset = stateToClass[state_games].deserialize(data, offset)
            some_games_dto.append(game)
        gamesDTO = GamesDTO(client_id=client_id, state_games=state_games, games_dto=some_games_dto)
        return gamesDTO, offset

    def set_state(self, state_games):
        self.state_games = state_games
        self.games_dto = list(map(lambda game: stateToClass[state_games].from_state(game), self.games_dto))

    def is_EOF(self):
        return False
    
    def get_client(self):
        return self.client_id
    
    def get_platform_count(self):
        count = {
            "windows": 0,
            "mac": 0,
            "linux": 0
        }
        for game in self.games_dto:
            platform = game.get_platform_count()
            count["windows"] += platform["windows"]
            count["mac"] += platform["mac"]
            count["linux"] += platform["linux"]
        return count

    def is_reviews(self):
        return False
    
    def is_games(self):
        return True
    
    def filter_games(self, filter_func):
        self.games_dto = list(filter(filter_func, self.games_dto))

    def to_result(self):
        if self.state_games == STATE_PLATFORM:
            return self.games_dto[0].to_result()
        games = []
        for game in self.games_dto:
            games.append(game.name)
        return Query2345ResultDTO(query=self.query, games=games)

    def from_raw(raw_dto: RawDTO, indexes):
        games_dto = []
        for game_raw in raw_dto.raw_data:
            games_dto.append(GameMinimalDTO.from_raw(game_raw, indexes))
        return GamesDTO(client_id=raw_dto.client_id, state_games=STATE_GAMES_MINIMAL, games_dto=games_dto)