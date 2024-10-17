from common.utils.utils import initialize_log
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.DTO.GameDTO import GameDTO
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.enums.StateGame import StateGame
from system.commonsSystem.handlerEOF.HandlerEOF import HandlerEOF
from system.commonsSystem.DTO.ResultQueryDTO import ResultQueryDTO
from system.commonsSystem.utils.utils import eof_calculator, handler_sigterm_default
from system.commonsSystem.utils.MessageHandler import MessageHandler

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

        self.handler_eof_games = HandlerEOF(broker =self.broker, node_id =self.id, target_name ="Games", total_nodes= self.total_nodes,
                            exchange_name =EXCHANGE_EOF_FILTERDECADE, next_queues =[QUEUE_FILTERDECADE_GROUPERTOPAVGTIME])
        self.broker.create_fanout_and_bind(name_exchange =EXCHANGE_EOF_FILTERDECADE, callback =eof_calculator(self.handler_eof_games))

        self.broker.create_queue(name =QUEUE_FILTERGENDER_FILTERDECADE, callback = MessageHandler.with_eof(self.handler_eof_games, self.filter_for_decade))
        self.broker.create_queue(name =QUEUE_FILTERDECADE_GROUPERTOPAVGTIME)

    def filter_for_decade(self, batch_game):
        new_games = {}
        for game in batch_game.games_dto:
            if self.decade in game.release_date:
                new_games[game.app_id] = [game.name, game.avg_playtime_forever]
        result_query = ResultQueryDTO(client_id =batch_game.client_id, data =new_games)
        
        self.broker.public_message(queue_name =QUEUE_FILTERDECADE_GROUPERTOPAVGTIME, message =result_query.serialize())
        self.handler_eof_games.add_data_process(len(batch_game.games_dto))
        self.handler_eof_games.add_data_sent(len(new_games))

    def run(self):
        self.broker.start_consuming()
