from common.utils.utils import initialize_log
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.DTO.GameDTO import GameDTO
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.DTO.enums.StateGame import StateGame
from system.commonsSystem.handlerEOF.HandlerEOF import HandlerEOF
from system.commonsSystem.DTO.ResultQueryDTO import ResultQueryDTO
from system.commonsSystem.utils.utils import eof_calculator, handler_sigterm_default

import logging
import os
import signal

QUEUE_FILTERGENDER_FILTERDECADE = "filterGender_filterDecade"
QUEUE_FILTERDECADE_GROUPERTOPAVGTIME = "filterDecade_grouperTopAvgTime"
EXCHANGE_EOF_FILTERDECADE = "Exchange_filterDecade"

DECADE = 2010

class FilterDecade:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.id = os.getenv("NODE_ID")
        self.total_nodes = int(os.getenv("TOTAL_NODES"))
        self.decade = str(DECADE)[0:3]
        self.broker = Broker()
        signal.signal(signal.SIGTERM, handler_sigterm_default(self.broker))
        self.broker.create_queue(name =QUEUE_FILTERGENDER_FILTERDECADE, callback = self.handler_filter_by_decade())
        self.broker.create_queue(name =QUEUE_FILTERDECADE_GROUPERTOPAVGTIME)

        self.handler_eof_games = HandlerEOF(broker =self.broker, node_id =self.id, target_name ="Games", total_nodes= self.total_nodes,
                            exchange_name =EXCHANGE_EOF_FILTERDECADE, next_queues =[QUEUE_FILTERDECADE_GROUPERTOPAVGTIME])
        self.broker.create_fanout_and_bind(name_exchange =EXCHANGE_EOF_FILTERDECADE, callback =eof_calculator(self.handler_eof_games))

    def handler_filter_by_decade(self):
        def handler_message(ch, method, properties, body):
            result_dto = DetectDTO(body).get_dto()
            if result_dto.operation_type == OperationType.OPERATION_TYPE_EOF_DTO:
                self.handler_eof_games.init_leader_and_push_eof(result_dto)
            else:
                self.filter_for_decade(result_dto)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_message
    
    def filter_for_decade(self, batch_game):
        new_games = {}
        for game in batch_game.games_dto:
            if self.decade in game.release_date:
                new_games[game.app_id] = [game.name, game.avg_playtime_forever]
        result_query = ResultQueryDTO(client_id =batch_game.client_id, data =new_games)
        self.broker.public_message(queue_name =QUEUE_FILTERDECADE_GROUPERTOPAVGTIME, message =result_query.serialize())
        self.handler_eof_games.add_data_process()
    
    def run(self):
        self.broker.start_consuming()
