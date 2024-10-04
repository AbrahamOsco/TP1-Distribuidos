from common.utils.utils import initialize_log
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.DTO.GameDTO import GameDTO
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.DTO.enums.StateGame import StateGame
import logging
import time as t
import os
from system.commonsSystem.protocol.ServerProtocol import ServerProtocol

QUEUE_FILTER_SELECTQ2345 = "filterbasic_selectq2345"
QUEUE_GAMESQ2345 = "GamesQ2345"

class SelectQ2345:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.broker = Broker()
        self.broker.create_queue(name =QUEUE_FILTER_SELECTQ2345, durable =True, callback = self.handler_callback())
        self.broker.create_queue(name =QUEUE_GAMESQ2345, durable = True)

    def handler_callback(self):
        def handler_message(ch, method, properties, body):
            result = DetectDTO(body).get_dto()
            if result.operation_type != OperationType.OPERATION_TYPE_GAMES_DTO:
                logging.info(f"TODO: HANDLER: EOF 🔚 🏮 🗡️")
            self.filter_for_q2345(result)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_message
    
    #TODO: Crear SelectsQ2345 y enviar eso en vez de GamesDTO
    def filter_for_q2345(self, batch_game: GamesDTO):
        games_dto = []      
        for game in batch_game.games_dto:
            games_dto.append(GameDTO(
                app_id=game.app_id, 
                name=game.name, 
                genres=game.genres, 
                release_date=game.release_date, 
                avg_playtime_forever=game.avg_playtime_forever
            ))
            
            logging.info(f"Game ID: {game.app_id} Name: {game.name} Gender: {game.genres} Year: {game.release_date} avg_playtime_forever: {game.avg_playtime_forever} 🐴 🏇 ")
        
        new_gamesDTO = GamesDTO(client_id=batch_game.client_id, state_games=StateGame.STATE_Q2345.value, games_dto=games_dto)
        self.broker.public_message(queue_name=QUEUE_GAMESQ2345, message=new_gamesDTO.serialize())
        logging.info(f"action: Send GamesDTO 🏑 to filter_gender | count: {len(new_gamesDTO.games_dto)} | result: success ✅")

    def run(self):
        self.broker.start_consuming()
        # self.broker.close() # Solo hacer el close cuando recibamos la signal y acabe todo ordenado!!. 

