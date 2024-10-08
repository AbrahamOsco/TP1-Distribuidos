from common.utils.utils import initialize_log
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.DTO.GameDTO import GameDTO
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.DTO.enums.StateGame import StateGame
from system.commonsSystem.handlerEOF.HandlerEOF import HandlerEOF
from system.commonsSystem.utils.utils import eof_calculator, handler_sigterm_default
from system.commonsSystem.utils.TopN import TopN
from system.commonsSystem.DTO.TopDTO import TopDTO
import logging
import os
import signal

QUEUE_FILTERDECADE_GROUPERTOPAVGTIME = "filterDecade_grouperTopAvgTime"
QUEUE_RESULTQ2_GATEWAY = "resultq2_gateway"

class GrouperTopAvgPlaytime:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.id = os.getenv("NODE_ID")
        self.total_nodes = int(os.getenv("TOTAL_NODES"))
        self.broker = Broker()
        signal.signal(signal.SIGTERM, handler_sigterm_default(self.broker))
        self.top_games = TopN(field_batch= lambda game: game.games_dto,
                            field_to_compare = lambda game: game.avg_playtime_forever, a_size = int(os.getenv("TOP_SIZE")))
        self.broker.create_queue(name =QUEUE_FILTERDECADE_GROUPERTOPAVGTIME, callback = self.handler_calculate_top_avg_playtime())
        self.broker.create_queue(name =QUEUE_RESULTQ2_GATEWAY)
        
    def handler_calculate_top_avg_playtime(self):
        def handler_message(ch, method, properties, body):
            result_dto = DetectDTO(body).get_dto()
            if result_dto.operation_type == OperationType.OPERATION_TYPE_EOF_DTO:
                top_gamesDTO = TopDTO(client_id =result_dto.client_id, results =self.top_games.get_top10())
                self.broker.public_message(queue_name =QUEUE_RESULTQ2_GATEWAY, message =top_gamesDTO.serialize() )
                logging.info(f"Recv EOF 🎖️{self.top_games.get_top10()}")
            else:
                self.top_games.update_top(result_dto)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_message
    
    def run(self):
        self.broker.start_consuming()
