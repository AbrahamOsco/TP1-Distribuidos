from common.utils.utils import initialize_log
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.DTO.GameDTO import GameDTO
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.enums.StateGame import StateGame
from system.commonsSystem.handlerEOF.HandlerEOF import HandlerEOF
from system.commonsSystem.utils.utils import eof_calculator, handler_sigterm_default
from system.commonsSystem.utils.MessageHandler import MessageHandler

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
        self.handler_eof_games = HandlerEOF(broker =self.broker, node_id =self.id, target_name ="Games", total_nodes =self.total_nodes,
                                exchange_name =EXCHANGE_EOF_SELECTQ2345, next_queues =[QUEUE_SELECTQ2345_FILTERGENDER])
        self.broker.create_queue(name =QUEUE_FILTER_SELECTQ2345, callback = MessageHandler.with_eof(self.handler_eof_games, self.select_for_q2345))
        self.broker.create_fanout_and_bind(name_exchange =EXCHANGE_EOF_SELECTQ2345, callback =eof_calculator(self.handler_eof_games))
        self.broker.create_queue(name =QUEUE_SELECTQ2345_FILTERGENDER)

    def select_for_q2345(self, batch_game: GamesDTO):
        new_gamesDTO = GamesDTO(client_id =batch_game.client_id, state_games =StateGame.STATE_Q2345.value, games_dto =batch_game.games_dto)
        self.broker.public_message(queue_name =QUEUE_SELECTQ2345_FILTERGENDER, message =new_gamesDTO.serialize())
        self.handler_eof_games.add_data_process(len(batch_game.games_dto))
        self.handler_eof_games.add_data_sent(len(batch_game.games_dto))


    def run(self):
        self.broker.start_consuming()

