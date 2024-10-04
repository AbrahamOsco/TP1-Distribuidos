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
import bisect

QUEUE_GAMESINDIEDECADEQ2 = "GamesIndieDecadeQ2"
QUEUE_RESULTQUERY2 = "result.query.2"
class Grouper():
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.broker = Broker()
        self.reset_list()
        self.broker.create_queue(name =QUEUE_GAMESINDIEDECADEQ2, durable =True, callback = self.handler_callback())
        self.broker.create_queue(name =QUEUE_RESULTQUERY2, durable =True)
        self.top_size = int(os.getenv("TOP_SIZE"))

    def reset_list(self):
        self.list = []
        self.min_time = 0

    def has_to_be_inserted(self, game):
        return (len(self.list) < self.top_size) or (int(game.avg_playtime_forever) > int(self.min_time))

    def handler_callback(self):
        def handler_message(ch, method, properties, body):
            result = DetectDTO(body).get_dto()
            if result.operation_type != OperationType.OPERATION_TYPE_GAMES_DTO:
                logging.info(f"TODO: HANDLER: EOF 🔚 🏮 🗡️")
            self.filter_for_grouper(result)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_message
    
    #TODO: Crear GroupersTopAveragePlayTimeDTO y enviar eso en vez de GamesDTO
    def filter_for_grouper(self, batch_game: GamesDTO):
        for game in batch_game.games_dto:
            if self.has_to_be_inserted(game):
                was_inserted = False
                for i in range(len(self.list)):
                    if game.avg_playtime_forever > self.list[i].avg_playtime_forever:
                        self.list.insert(i, game)
                        was_inserted = True
                        break
                
                if not was_inserted:
                    self.list.append(game)

                
                if len(self.list) > self.top_size:
                    self.list.pop()
                
                self.min_time = self.list[-1].avg_playtime_forever

        if len(self.list) == self.top_size:
            new_games_indie_DTO = GamesDTO(client_id=batch_game.client_id, state_games=StateGame.STATE_TOP_AVERAGE_PLAYTIME.value, games_dto=self.list)
            self.broker.public_message(queue_name=QUEUE_RESULTQUERY2, message=new_games_indie_DTO.serialize())
            logging.info(f"action: Send Indie GamesDTO 🏑 to gateway | count: {len(new_games_indie_DTO.games_dto)} | result: success ✅")
           
    def run(self):
        self.broker.start_consuming()