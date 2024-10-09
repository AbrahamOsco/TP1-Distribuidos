from common.utils.utils import initialize_log
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO
from system.commonsSystem.DTO.ReviewDTO import ReviewDTO
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.DTO.enums.StateGame import StateGame
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from common.utils.utils import ALL_GAMES_WAS_SENT
from system.commonsSystem.handlerEOF.HandlerEOF import HandlerEOF
from system.commonsSystem.utils.utils import eof_calculator, handler_sigterm_default

import logging
import os
import signal

QUEUE_FILTERGENDER_SELECTIDNAME = "filterGender_selectIDName"
QUEUE_SELECTIDNAME_MONITORSTORAGEQ3 = "selectIDName_monitorStorageQ3"

EXCHANGE_EOF_SELECTIDNAME = "Exchange_selectIDName"

class SelectIDName:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.id = os.getenv("NODE_ID")
        self.total_nodes = int(os.getenv("TOTAL_NODES"))
        self.broker = Broker()
        signal.signal(signal.SIGTERM, handler_sigterm_default(self.broker))
        self.broker.create_queue(name =QUEUE_FILTERGENDER_SELECTIDNAME, callback = self.handler_select_IDName())
        self.broker.create_queue(name =QUEUE_SELECTIDNAME_MONITORSTORAGEQ3)
        
        self.handler_eof_games = HandlerEOF(broker =self.broker, node_id =self.id, target_name ="Games", total_nodes= self.total_nodes,
                            exchange_name =EXCHANGE_EOF_SELECTIDNAME, next_queues =[QUEUE_SELECTIDNAME_MONITORSTORAGEQ3])
        self.broker.create_fanout_and_bind(name_exchange =EXCHANGE_EOF_SELECTIDNAME, callback =eof_calculator(self.handler_eof_games))


    def handler_select_IDName(self):
        def handler_message(ch, method, properties, body):
            result_dto = DetectDTO(body).get_dto()
            if result_dto.operation_type == OperationType.OPERATION_TYPE_EOF_DTO:
                self.handler_eof_games.init_leader_and_push_eof(result_dto)
            else:
                self.select_id_and_name(result_dto)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_message
    
    def select_id_and_name(self, batch_data):
        new_gamesDTO = GamesDTO(client_id =batch_data.client_id, state_games =StateGame.STATE_ID_NAME.value, games_dto =batch_data.games_dto)
        self.broker.public_message(queue_name =QUEUE_SELECTIDNAME_MONITORSTORAGEQ3, message =new_gamesDTO.serialize() )
        self.handler_eof_games.add_new_processing()

    def run(self):
        self.broker.start_consuming()
