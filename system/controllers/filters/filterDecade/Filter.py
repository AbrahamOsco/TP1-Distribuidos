import os
from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_PLAYTIME

class Filter(Node):
    def __init__(self):
        super().__init__()
        self.decade = int(os.getenv("DECADE"))

    def is_correct_decade(self, date):
        if len(date.split(', ')) < 2:
            return False
        year = int(date.split(', ')[1])
        return year >= self.decade and year < self.decade + 10

    def send_game(self, data:GamesDTO):
        data.set_state(STATE_PLAYTIME)
        self.broker.public_message(exchange_name=self.sink, message=data.serialize(), routing_key="default")

    def process_data(self, data:GamesDTO):
        data.filter_games(lambda x: self.is_correct_decade(x.release_date))
        if len(data.games_dto) > 0:
            self.send_game(data)