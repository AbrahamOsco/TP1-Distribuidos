from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_GENRE, STATE_Q2345
from system.commonsSystem.DTO.EOFDTO import EOFDTO
from system.commonsSystem.DTO.enums.OperationType import OperationType
import os

class Filter(Node):
    def __init__(self):
        super().__init__()
        self.genders = os.getenv("GENDERS").split(',')

    def is_gender(self, genders, wanted_gender):
        return wanted_gender in genders.split(',')
    
    def send_eof(self, data):
        client = data.get_client()
        for gender in self.genders:
            self.broker.public_message(sink=self.sink, message=EOFDTO(OperationType.OPERATION_TYPE_GAMES_EOF_DTO.value, client, False).serialize(), routing_key=gender)
    
    def send_game(self, data:GamesDTO, gender):
        data.set_state(STATE_GENRE)
        self.broker.public_message(sink=self.sink, routing_key=gender, message=data.serialize())

    def update_amount_sent_by_node(self,client_id, gender, amount=0):
        if client_id not in self.amount_sent_by_node:
            self.amount_sent_by_node[client_id] = {}
        if gender not in self.amount_sent_by_node[client_id]:
            self.amount_sent_by_node[client_id][gender] = 0
        
        self.amount_sent_by_node[client_id][gender] += amount

    def process_data(self, data: GamesDTO):
        self.update_amount_received_by_node(data.get_client(), data.get_amount())
        for gender in self.genders:
            games_in_gender = []
            for game in data.games_dto:
                if self.is_gender(game.genres, gender):
                    games_in_gender.append(game) 
            if len(games_in_gender) > 0:
                self.send_game(GamesDTO(client_id=data.client_id, state_games=STATE_Q2345, games_dto=games_in_gender), gender)
            self.update_amount_sent_by_node(data.get_client(), gender, len(games_in_gender))
          