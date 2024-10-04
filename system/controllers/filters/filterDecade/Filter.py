import os
import logging
from common.utils.utils import initialize_log
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.DTO.GameDTO import GameDTO
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.enums.StateGame import StateGame
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.DecadeDTO import DecadeDTO

QUEUE_GAMESINDIEQ2 = "GamesIndieQ2"
QUEUE_GAMESINDIEDECADEQ2 = "GamesIndieDecadeQ2"
class Filter():
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.broker = Broker()
        self.broker.create_queue(name =QUEUE_GAMESINDIEQ2, durable =True, callback = self.handler_callback())
        self.broker.create_queue(name =QUEUE_GAMESINDIEDECADEQ2, durable =True)
        self.decade = int(os.getenv("DECADE"))

    def is_correct_decade(self, date):
        year = int(date.split(', ')[1])
        return year >= self.decade and year < (self.decade + 10)
    

    def handler_callback(self):
        def handler_message(ch, method, properties, body):
            result = DetectDTO(body).get_dto()
            if result.operation_type != OperationType.OPERATION_TYPE_GAMES_DTO:
                logging.info(f"TODO: HANDLER: EOF 🔚 🏮 🗡️")
            self.filter_for_decade(result)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_message
    
    #TODO: Crear FiltersDecadeDTO y enviar eso en vez de GamesDTO
    def filter_for_decade(self, batch_game: GamesDTO):
        games_indie_dto = []
        for game in batch_game.games_dto:
            if self.is_correct_decade(game.release_date):
                games_indie_dto.append(GameDTO(
                    app_id=game.app_id, 
                    name=game.name,
                    avg_playtime_forever=game.avg_playtime_forever
                ))

        if games_indie_dto:
            new_games_indie_DTO = GamesDTO(client_id=batch_game.client_id, state_games=StateGame.STATE_DECADE.value, games_dto=games_indie_dto)
            self.broker.public_message(queue_name=QUEUE_GAMESINDIEDECADEQ2, message=new_games_indie_DTO.serialize())
            logging.info(f"action: Send Indie GamesDTO 🏑 to grouper_top_average_playtime | count: {len(new_games_indie_DTO.games_dto)} | result: success ✅")
           
    def run(self):
        self.broker.start_consuming()