from common.utils.utils import initialize_log
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.DTO.GameDTO import GameDTO
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.DTO.enums.StateGame import StateGame
from system.commonsSystem.handlerEOF.HandlerEOF import HandlerEOF
from system.commonsSystem.utils.utils import eof_calculator, handler_sigterm_default

import logging
import os
import signal

QUEUE_FILTER_SELECTQ2345 = "filterBasic_selectq2345"
QUEUE_SELECTQ2345_FILTERGENDER = "selectq2345_filterGender"
EXCHANGE_EOF_SELECTQ2345 = "Exchange_selectq2345"

class SelectQ2345:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.id = os.getenv("NODE_ID")
        self.total_nodes = int(os.getenv("TOTAL_NODES"))

        self.broker = Broker()
        signal.signal(signal.SIGTERM, handler_sigterm_default(self.broker))
        self.broker.create_queue(name =QUEUE_FILTER_SELECTQ2345, callback = self.handler_select_for_q2345())
        self.broker.create_queue(name =QUEUE_SELECTQ2345_FILTERGENDER)

        self.handler_eof_games = HandlerEOF(broker =self.broker, node_id =self.id, target_name ="Games", total_nodes =self.total_nodes,
                                exchange_name =EXCHANGE_EOF_SELECTQ2345, next_queues =[QUEUE_SELECTQ2345_FILTERGENDER])
        self.broker.create_fanout_and_bind(name_exchange =EXCHANGE_EOF_SELECTQ2345, callback =eof_calculator(self.handler_eof_games))

    def handler_select_for_q2345(self):
        def handler_message(ch, method, properties, body):
            result_dto = DetectDTO(body).get_dto()
            if result_dto.operation_type == OperationType.OPERATION_TYPE_EOF_DTO:
                self.handler_eof_games.init_leader_and_push_eof(result_dto)
            else:
                self.filter_for_q2345(result_dto)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_message
    
    def filter_for_q2345(self, batch_game: GamesDTO):
        new_gamesDTO = GamesDTO(client_id =batch_game.client_id, state_games =StateGame.STATE_Q2345.value, games_dto =batch_game.games_dto)
        self.broker.public_message(queue_name =QUEUE_SELECTQ2345_FILTERGENDER, message =new_gamesDTO.serialize())
        self.handler_eof_games.add_new_processing()

    def run(self):
        self.broker.start_consuming()

