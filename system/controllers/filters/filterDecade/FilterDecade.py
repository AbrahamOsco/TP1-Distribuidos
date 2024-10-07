from common.utils.utils import initialize_log
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.DTO.GameDTO import GameDTO
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.DTO.enums.StateGame import StateGame
from system.commonsSystem.handlerEOF.HandlerEOF import HandlerEOF
import logging
import os
import signal

QUEUE_FILTERGENDER_FILTERDECADE = "filterGender_filterDecade"
QUEUE_FILTERDECADE_GROUPERTOPAVGTIME = "filterDecade_grouperTopAvgTime"
EXCHANGE_EOF_FILTERDECADE = "Exchange_filterDecade"

DECADE = 2010

class FilterDecade():
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.id = os.getenv("NODE_ID")
        self.total_nodes = int(os.getenv("TOTAL_NODES"))
        signal.signal(signal.SIGTERM, self.handler_sigterm)
        self.decade = DECADE
        self.broker = Broker()
        self.broker.create_queue(name =QUEUE_FILTERGENDER_FILTERDECADE, callback = self.filter_by_decade())
        self.broker.create_queue(name =QUEUE_FILTERDECADE_GROUPERTOPAVGTIME)

        self.broker.create_fanout_and_bind(name_exchange =EXCHANGE_EOF_FILTERDECADE, callback =self.callback_eof_calculator())
        self.handler_eof_games = HandlerEOF(broker =self.broker, node_id =self.id, target_name ="Games", total_nodes= self.total_nodes,
                            exchange_name =EXCHANGE_EOF_FILTERDECADE, next_queues =[QUEUE_FILTERDECADE_GROUPERTOPAVGTIME])

    def callback_eof_calculator(self):
        def handler_message(ch, method, properties, body):
            result_dto = DetectDTO(body).get_dto()
            self.handler_eof_games.run(calculatorDTO=result_dto)
            ch.basic_ack(delivery_tag =method.delivery_tag)
        return handler_message

    def is_correct_decade(self, relase_date):
        parts = relase_date.strip().split()
        year = None
        if len(parts) == 3:
            year = int(parts[2])
        elif len(parts) == 2:
            year = int(parts[1])
        
        return year >= self.decade and year < (self.decade + 10)
    

    def filter_by_decade(self):
        def handler_message(ch, method, properties, body):
            result_dto = DetectDTO(body).get_dto()
            if result_dto.operation_type == OperationType.OPERATION_TYPE_EOF_INITIAL_DTO:
                self.handler_eof_games.init_lider_and_push_eof(result_dto)
                logging.info(f"TODO: HANDLER: EOF 🔚 🏮 🪓 🐺 🗡️")
            else:
                self.filter_for_decade(result_dto)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_message
    
    def filter_for_decade(self, batch_game):
        some_games = []
        for game in batch_game.games_dto:
            if self.is_correct_decade(game.release_date):
                some_games.append(GameDTO(
                    app_id=game.app_id, 
                    name=game.name,
                    avg_playtime_forever=game.avg_playtime_forever
                ))
        gamesDTO = GamesDTO(client_id =batch_game.client_id, state_games =StateGame.STATE_DECADE.value, games_dto =some_games)
        self.broker.public_message(queue_name =QUEUE_FILTERDECADE_GROUPERTOPAVGTIME, message =gamesDTO.serialize())
        logging.info(f"action: Send Games To 🔥 🌟  | count: { len(gamesDTO.games_dto) } | result: success ✅")
        self.handler_eof_games.add_new_processing()
    
    def run(self):
        self.broker.start_consuming()

    def handler_sigterm(self, signum, frame):
        logging.info(f"action:⚡signal SIGTERM {signum} was received | result: sucess ✅ ")
        self.broker.close()
