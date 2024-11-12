from system.commonsSystem.DTO.GamesDTO import STATE_IDNAME
from system.commonsSystem.DTO.GameIDNameDTO import GameIDNameDTO
from system.commonsSystem.node.dualInputNode import DualInputNode
import os
import logging

class Storage(DualInputNode):
    def __init__(self):
        super().__init__(500)
        self.percentile = float(os.getenv("PERCENTILE", 0.9))

    def send_result(self, client_id):
        values = sorted(self.data.list[client_id].items(), key=lambda item: (item[1], item[0]))
        index = int(self.percentile * len(values)) -1
        logging.info(f"Percentile cal. Total games: {len(values)}. Sending: {len(values[index:])}")
        games_to_send = []
        for app_id, _ in values[index:]:
            games_to_send.append(GameIDNameDTO(app_id=app_id, name=self.data.games[client_id][app_id]))
            if len(games_to_send) > 50:
                self.send_games(client_id, games_to_send, STATE_IDNAME, query=5)
                games_to_send = []
        if len(games_to_send) > 0:
            self.send_games(client_id, games_to_send, STATE_IDNAME, query=5)