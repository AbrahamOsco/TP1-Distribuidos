from system.commonsSystem.node.dualInputNode import DualInputNode
from system.commonsSystem.DTO.GameReviewedDTO import GameReviewedDTO
from system.commonsSystem.DTO.GamesDTO import STATE_REVIEWED

class Storage(DualInputNode):
    def __init__(self):
        super().__init__(2500)

    def send_result(self, client_id):
        games = []
        for app_id in self.data.list[client_id]:
            games.append(GameReviewedDTO(app_id, self.data.games[client_id][app_id], self.data.list[client_id][app_id]))
            if len(games) == 250:
                self.send_games(client_id, games, STATE_REVIEWED, 3)
                games = []
        if len(games) > 0:
            self.send_games(client_id, games, STATE_REVIEWED, 3)