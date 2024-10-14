import os
from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_PLAYTIME, STATE_IDNAME

class Grouper(Node):
    def __init__(self):
        super().__init__()
        self.reset_list()
        self.top_size = int(os.getenv("TOP_SIZE"))

    def reset_list(self, client_id=None):
        if client_id is None:
            self.list = {}
            self.min_time = {}
        else:
            del self.list[client_id]
            del self.min_time[client_id]

    def pre_eof_actions(self, client_id):
        games = GamesDTO(client_id=client_id, state_games=STATE_PLAYTIME, games_dto=self.list[client_id], query=2)
        games.set_state(STATE_IDNAME)
        self.send_result(games)
        self.reset_list(client_id)

    def has_to_be_inserted(self, game, current_client):
        return len(self.list[current_client]) < self.top_size or game.avg_playtime_forever > self.min_time[current_client]
    
    def send_result(self, games):
        self.broker.public_message(sink=self.sink, message=games.serialize(), routing_key="default")

    def process_data(self, data: GamesDTO):
        current_client = data.get_client()
        self.eof.update_amount_received_by_node(data.get_client(), data.get_amount())
        if current_client not in self.list:
            self.list[current_client] = []
            self.min_time[current_client] = 0
        for game in data.games_dto:
            if self.has_to_be_inserted(game, current_client):
                inserted = False
                for i in range(len(self.list[current_client])):
                    if game.avg_playtime_forever > self.list[current_client][i].avg_playtime_forever:
                        self.list[current_client].insert(i, game)
                        inserted = True
                        break
                if not inserted:
                    self.list[current_client].append(game)
                if len(self.list[current_client]) > self.top_size:
                    self.list[current_client].pop()
                self.min_time[current_client] = self.list[current_client][-1].avg_playtime_forever

                if inserted and len(self.list[current_client]) <= self.top_size:
                    self.eof.update_amount_sent_by_node(data.get_client(), 1)