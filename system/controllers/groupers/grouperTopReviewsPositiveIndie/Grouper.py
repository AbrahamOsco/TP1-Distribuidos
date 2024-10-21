import os
from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_IDNAME, STATE_REVIEWED

class Grouper(Node):
    def __init__(self):
        super().__init__()
        self.reset_list()
        self.top_size = int(os.getenv("TOP_SIZE"))

    def reset_list(self, client_id=None):
        if client_id is None:
            self.list = {}
            self.min_time = {}
            self.counters = {}
        else:
            del self.list[client_id]
            del self.min_time[client_id]
            del self.counters[client_id]

    def pre_eof_actions(self, client_id):
        if client_id not in self.list:
            return
        games = GamesDTO(client_id=client_id, state_games=STATE_REVIEWED, games_dto=self.list[client_id], query=3, global_counter=self.counters[client_id])
        games.set_state(STATE_IDNAME)
        self.send_result(games)
        self.reset_list(client_id)

    def has_to_be_inserted(self, game, client_id):
        return len(self.list[client_id]) < self.top_size or game.reviews > self.min_time[client_id]

    def send_result(self, games):
        self.broker.public_message(sink=self.sink, message=games.serialize(), routing_key="default")

    def process_data(self, data: GamesDTO):
        client_id = data.get_client()
        if client_id not in self.list:
            self.list[client_id] = []
            self.min_time[client_id] = 0
        self.counters[client_id] = data.global_counter
        for game in data.games_dto:
            if self.has_to_be_inserted(game, client_id):
                inserted = False
                for i in range(len(self.list[client_id])):
                    if game.reviews > self.list[client_id][i].reviews:
                        self.list[client_id].insert(i, game)
                        inserted = True
                        break
                if not inserted:
                    self.list[client_id].append(game)
                if len(self.list[client_id]) > self.top_size:
                    self.list[client_id].pop()
                self.min_time[client_id] = self.list[client_id][-1].reviews