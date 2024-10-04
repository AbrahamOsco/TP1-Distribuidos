from common.utils.utils import initialize_log
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_PLATFORM
from system.commonsSystem.DTO.GameDTO import GameDTO
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.DetectDTO import DetectDTO
import signal
import logging
import time as t
import os
from system.commonsSystem.protocol.ServerProtocol import ServerProtocol

QUEUE_FILTER_SELECTQ1 = "filterbasic_selectq1"
QUEUE_SELECTQ1_PLATFORMCOUNTER = "selectq1_platformCounter"

class SelectQ1:
    
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.broker = Broker()
        signal.signal(signal.SIGTERM, self.handler_sigterm)
        self.broker.create_queue(name =QUEUE_FILTER_SELECTQ1, durable =True, callback = self.handler_callback())
        self.broker.create_queue(name =QUEUE_SELECTQ1_PLATFORMCOUNTER, durable =True)
    
    def handler_callback(self):
        def handler_message(ch, method, properties, body):
            result = DetectDTO(body).get_dto()
            if result.operation_type != OperationType.OPERATION_TYPE_GAMES_DTO:
                logging.info(f"TODO: HANDLER: EOF 🔚 🏮 🗡️")
            self.filter_platform(result)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_message
    
    def filter_platform(self, batch_game: GamesDTO):
        games_dto = []
        for game in batch_game.games_dto:
            games_dto.append(GameDTO(windows=game.windows, mac=game.mac, linux=game.linux))
            logging.info(f"Windows: {game.windows} Linux: {game.linux} Mac: {game.mac} 🐴 🏇 ")
        new_gamesDTO = GamesDTO(client_id =batch_game.client_id, state_games = STATE_PLATFORM, games_dto = games_dto)
        self.broker.public_message(queue_name =QUEUE_SELECTQ1_PLATFORMCOUNTER,  message = new_gamesDTO.serialize())
        logging.info(f"action: Send GamesDTO 🏑 to platform_counter | count: {len(new_gamesDTO.games_dto)} | result: success ✅")

    def handler_sigterm(self, signum, frame):
        logging.info(f"action:⚡signal SIGTERM {signum} was received | result: sucess ✅ ")
        self.broker.close()

    def run(self):
        self.broker.start_consuming()
