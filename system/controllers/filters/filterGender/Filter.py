import os
import logging
from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_DECADE

class Filter(Node):
    def __init__(self):
        super().__init__()
        self.genders = os.getenv("GENDERS").split(',')

    def is_gender(self, genders, wanted_gender):
        return wanted_gender in genders.split(',')
    
    def send_game(self, data:GamesDTO, gender):
        data.set_state(STATE_DECADE)
        self.broker.public_message(exchange_name=self.sink, routing_key=gender, message=data.serialize())

    def process_data(self, data: GamesDTO):
        for gender in self.genders:
            games_in_gender = []
            for game in data.games_dto:
                if self.is_gender(game.genres, gender):
                    games_in_gender.append(game)
            if len(games_in_gender) > 0:
                self.send_game(GamesDTO(client_id=data.client_id, state_games=STATE_DECADE, games_dto=games_in_gender), gender)