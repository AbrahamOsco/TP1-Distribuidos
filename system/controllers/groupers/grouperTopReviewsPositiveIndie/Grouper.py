import logging
import os
from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_IDNAME, STATE_REVIEWED
from system.commonsSystem.DTO.GameIDNameDTO import GameIDNameDTO

class Grouper(Node):
    def __init__(self):
        super().__init__()
        self.reset_list()
        self.top_size = int(os.getenv("TOP_SIZE"))

    def reset_list(self):
        self.list = []
        self.min_time = 0
        self.current_client = 0

    def pre_eof_actions(self, client_id):
        self.send_result()
        self.reset_list()

    def has_to_be_inserted(self, game):
        return len(self.list) < self.top_size or game.reviews > self.min_time

    def send_result(self):
        games = GamesDTO(client_id=self.current_client, state_games=STATE_REVIEWED, games_dto=self.list, query=3)
        games.set_state(STATE_IDNAME)
        self.broker.public_message(sink=self.sink, message=games.serialize(), routing_key="default")

    def process_data(self, data: GamesDTO):
        self.current_client = data.client_id
        self.update_amount_received_by_node(data.get_client(), data.get_amount())
        for game in data.games_dto:
            if self.has_to_be_inserted(game):
                inserted = False
                for i in range(len(self.list)):
                    if game.reviews > self.list[i].reviews:
                        self.list.insert(i, game)
                        inserted = True
                        break
                if not inserted:
                    self.list.append(game)
                if len(self.list) > self.top_size:
                    self.list.pop()
                self.min_time = self.list[-1].reviews

                if inserted and len(self.list) <= self.top_size:
                    self.update_amount_sent_by_node(data.get_client(), 1)