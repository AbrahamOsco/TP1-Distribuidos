from system.commonsSystem.DTO.enums.OperationType import OperationType
from common.utils.utils import initialize_log, ALL_GAMES_WAS_SENT
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_PLATFORM
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.handlerEOF.HandlerEOF import HandlerEOF
from system.commonsSystem.DTO.PlatformDTO import PlatformDTO
from system.commonsSystem.utils.utils import handler_sigterm_default
import os
import logging
import signal 

QUEUE_SELECTQ1_PLATFORMCOUNTER = "selectq1_platformCounter"
QUEUE_PLATFORMCOUNTER_REDUCER = "platformCounter_platformReducer"
EXCHANGE_EOF_PLATFORM_COUNTER = "Exchange_platformCounter"

class PlatformCounter:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.id = os.getenv("NODE_ID")
        self.total_nodes = int(os.getenv("TOTAL_NODES"))

        self.platform = PlatformDTO()
        self.registered_client = False
        self.broker = Broker()
        signal.signal(signal.SIGTERM, handler_sigterm_default(self.broker))
        self.broker.create_queue(name =QUEUE_SELECTQ1_PLATFORMCOUNTER, callback =self.handler_count_platforms())
        self.broker.create_queue(name =QUEUE_PLATFORMCOUNTER_REDUCER)

        self.broker.create_fanout_and_bind(name_exchange =EXCHANGE_EOF_PLATFORM_COUNTER, callback =self.callback_eof_calculator())
        self.handler_eof_games = HandlerEOF(broker =self.broker, node_id =self.id, target_name ="Games", total_nodes= self.total_nodes,
                                exchange_name =EXCHANGE_EOF_PLATFORM_COUNTER, next_queues =[QUEUE_PLATFORMCOUNTER_REDUCER])

    def callback_eof_calculator(self):
        def handler_message(ch, method, properties, body):
            result_dto = DetectDTO(body).get_dto()
            self.handler_eof_games.run(calculatorDTO =result_dto, auto_send =False, dto_to_send =self.platform)
            self.handler_eof_games.try_send_partial_data()
            ch.basic_ack(delivery_tag =method.delivery_tag)
        return handler_message

    def handler_count_platforms(self):
        def handler_message(ch, method, properties, body):
            result_dto = DetectDTO(body).get_dto()
            if result_dto.operation_type == OperationType.OPERATION_TYPE_EOF_DTO:
                self.handler_eof_games.init_leader_and_push_eof(result_dto)  
            else:
                self.count_platforms(result_dto)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_message

    def count_platforms(self, gamesDTO:GamesDTO):
        if not self.registered_client:
            self.platform.client_id = gamesDTO.client_id
            self.registered_client = True
        for a_game in gamesDTO.games_dto:
            self.platform.windows += a_game.windows
            self.platform.linux += a_game.linux
            self.platform.mac += a_game.mac
        self.handler_eof_games.add_new_processing()

    def run(self):
        self.broker.start_consuming()
