from system.commonsSystem.node.dualInputNode import DualInputNode
from system.commonsSystem.DTO.GameReviewedDTO import GameReviewedDTO
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_REVIEWED

class Storage(DualInputNode):
    def __init__(self):
        super().__init__()

    def send_result(self, client_id):
        games = []
        for app_id in self.list[client_id]:
            games.append(GameReviewedDTO(app_id, self.games[client_id][app_id], self.list[client_id][app_id]))
            if len(games) == 25:
                self.send_games(client_id, games, STATE_REVIEWED, 3)
                games = []
        if len(games) > 0:
            self.send_games(client_id, games, STATE_REVIEWED, 3)