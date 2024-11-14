from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_GENRE, STATE_Q2345
from system.commonsSystem.node.routingPolicies.RoutingOneToMany import RoutingOneToMany
import os

class Filter(Node):
    def __init__(self):
        self.genders = os.getenv("GENDERS").split(',')
        super().__init__(RoutingOneToMany(self.genders))

    def is_gender(self, genders, wanted_gender):
        return wanted_gender in genders.split(',')
    
    def send_game(self, data:GamesDTO, gender):
        data.set_state(STATE_GENRE)
        self.broker.public_message(sink=self.sink, routing_key=gender, message=data.serialize())

    def process_data(self, data: GamesDTO):
        for gender in self.genders:
            games_in_gender = []
            for game in data.games_dto:
                if self.is_gender(game.genres, gender):
                    games_in_gender.append(game) 
            if len(games_in_gender) > 0:
                self.send_game(GamesDTO(client_id=data.get_client(), state_games=STATE_Q2345, games_dto=games_in_gender, global_counter=data.global_counter), gender)