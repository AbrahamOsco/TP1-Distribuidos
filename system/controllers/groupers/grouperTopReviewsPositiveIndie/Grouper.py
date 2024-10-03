import logging
import os
from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.GamesDTO import GamesDTO

class Grouper(Node):
    def __init__(self):
        super().__init__()
        self.reset_list()
        self.top_size = int(os.getenv("TOP_SIZE"))

    def reset_list(self):
        self.list = []
        self.min_time = 0

    def pre_eof_actions(self):
        self.send_result()
        self.reset_list()

    def has_to_be_inserted(self, game):
        return len(self.list) < self.top_size or game.reviews > self.min_time
    
    def send_result(self):
        logging.info(f"action: result | list: {self.list}")
        # self.broker.public_message(sink=self.sink, message=self.list, routing_key="default")

    def process_data(self, data: GamesDTO):
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