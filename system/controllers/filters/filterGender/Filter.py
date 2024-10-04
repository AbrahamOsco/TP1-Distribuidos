import os
import logging
from common.utils.utils import initialize_log
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.DTO.GameDTO import GameDTO
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.enums.StateGame import StateGame
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.DecadeDTO import DecadeDTO

QUEUE_GAMESQ2345 = "GamesQ2345"
QUEUE_GAMESINDIEQ2 = "GamesIndieQ2"
QUEUE_GAMESINDIEQ3 = "GamesIndieQ3"
QUEUE_GAMESACTIONQ45 = "GamesActionQ45"
class Filter():
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.broker = Broker()
        self.broker.create_queue(name =QUEUE_GAMESQ2345, durable =True, callback = self.handler_callback())
        self.broker.create_queue(name =QUEUE_GAMESINDIEQ2, durable =True)
        self.broker.create_queue(name =QUEUE_GAMESINDIEQ3, durable =True)
        self.broker.create_queue(name =QUEUE_GAMESACTIONQ45, durable =True)

        self.genres = os.getenv("GENDERS").split(',')

    def handler_callback(self):
        def handler_message(ch, method, properties, body):
            result = DetectDTO(body).get_dto()
            if result.operation_type != OperationType.OPERATION_TYPE_GAMES_DTO:
                logging.info(f"TODO: HANDLER: EOF 🔚 🏮 🗡️")
            self.filter_for_gender(result)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_message
    
    #TODO: Crear FiltersGenderDTO y enviar eso en vez de GamesDTO
    def filter_for_gender(self, batch_game: GamesDTO):
        games_indie_dto = []
        games_action_dto = []

        for game in batch_game.games_dto:
            if "Indie" in game.genres:
                games_indie_dto.append(GameDTO(
                    app_id=game.app_id, 
                    name=game.name,  
                    release_date=game.release_date, 
                    avg_playtime_forever=game.avg_playtime_forever
                ))

            if "Action" in game.genres:
                games_action_dto.append(GameDTO(
                    app_id=game.app_id, 
                    name=game.name,  
                    release_date=game.release_date, 
                    avg_playtime_forever=game.avg_playtime_forever
                ))

        if games_indie_dto:
            new_games_indie_DTO = GamesDTO(client_id=batch_game.client_id, state_games=StateGame.STATE_GENDER.value, games_dto=games_indie_dto)
            self.broker.public_message(queue_name=QUEUE_GAMESINDIEQ2, message=new_games_indie_DTO.serialize())
            logging.info(f"action: Send Indie GamesDTO 🏑 to filter_decade | count: {len(new_games_indie_DTO.games_dto)} | result: success ✅")
            self.broker.public_message(queue_name=QUEUE_GAMESINDIEQ3, message=new_games_indie_DTO.serialize())
            logging.info(f"action: Send Indie GamesDTO 🏑 to select_id_name | count: {len(new_games_indie_DTO.games_dto)} | result: success ✅")
           

        if games_action_dto:
            new_games_action_DTO = GamesDTO(client_id=batch_game.client_id, state_games=StateGame.STATE_GENDER.value, games_dto=games_action_dto)
            self.broker.public_message(queue_name=QUEUE_GAMESACTIONQ45, message=new_games_action_DTO.serialize())
            logging.info(f"action: Send Action GamesDTO 🎮 to select_id_name | count: {len(new_games_action_DTO.games_dto)} | result: success ✅")


    def run(self):
        self.broker.start_consuming()