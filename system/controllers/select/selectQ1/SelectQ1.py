from common.utils.utils import initialize_log, ALL_GAMES_WAS_SENT, ALL_REVIEWS_WAS_SENT
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_PLATFORM
from system.commonsSystem.DTO.GameDTO import GameDTO
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.handlerEOF.HandlerEOF import HandlerEOF
import signal
import logging
import os

QUEUE_FILTER_SELECTQ1 = "filterBasic_selectq1"
QUEUE_SELECTQ1_PLATFORMCOUNTER = "selectq1_platformCounter"
EXCHANGE_EOF_SELECTQ1 = "Exchange_selectq1"

class SelectQ1:
    
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.id = os.getenv("NODE_ID")
        self.total_nodes = int(os.getenv("TOTAL_NODES"))
        signal.signal(signal.SIGTERM, self.handler_sigterm)
        
        self.broker = Broker()
        self.broker.create_queue(name =QUEUE_FILTER_SELECTQ1, callback = self.handler_filter_platforms())
        self.broker.create_queue(name =QUEUE_SELECTQ1_PLATFORMCOUNTER)

        self.broker.create_fanout_and_bind(name_exchange =EXCHANGE_EOF_SELECTQ1, callback =self.callback_eof_calculator())
        self.handler_eof_games = HandlerEOF(broker =self.broker, node_id =self.id, target_name ="Games", total_nodes= self.total_nodes,
                                exchange_name =EXCHANGE_EOF_SELECTQ1, next_queues =[QUEUE_SELECTQ1_PLATFORMCOUNTER])
    
    def callback_eof_calculator(self):
        def handler_message(ch, method, properties, body):
            result_dto = DetectDTO(body).get_dto()
            self.handler_eof_games.run(calculatorDTO=result_dto)
            ch.basic_ack(delivery_tag =method.delivery_tag)
        return handler_message

    def handler_filter_platforms(self):
        def handler_message(ch, method, properties, body):
            result_dto = DetectDTO(body).get_dto()
            if result_dto.operation_type == OperationType.OPERATION_TYPE_EOF_INITIAL_DTO and result_dto.old_operation_type == ALL_REVIEWS_WAS_SENT:
                logging.info(f"Action: Recv Reviews EOF ! 📄📄📄 | result: success ✅") # TODO: delete el if y esta linea
            elif result_dto.operation_type == OperationType.OPERATION_TYPE_EOF_INITIAL_DTO and result_dto.old_operation_type == ALL_GAMES_WAS_SENT:
                self.handler_eof_games.init_lider_and_push_eof(result_dto)
            else: 
                self.filter_platforms(result_dto)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_message
    
    def filter_platforms(self, batch_game: GamesDTO):
        games_dto = []
        for game in batch_game.games_dto:
            games_dto.append(GameDTO(windows=game.windows, mac=game.mac, linux=game.linux))
        new_gamesDTO = GamesDTO(client_id =batch_game.client_id, state_games = STATE_PLATFORM, games_dto = games_dto)
        self.broker.public_message(queue_name =QUEUE_SELECTQ1_PLATFORMCOUNTER,  message = new_gamesDTO.serialize())
        self.handler_eof_games.add_new_processing()
        #logging.info(f"action: Send GamesDTO 🏑 to platform_counter | count: {len(new_gamesDTO.games_dto)} | result: success ✅")

    def handler_sigterm(self, signum, frame):
        logging.info(f"action:⚡signal SIGTERM {signum} was received | result: sucess ✅ ")
        self.broker.close()

    def run(self):
        self.broker.start_consuming()
