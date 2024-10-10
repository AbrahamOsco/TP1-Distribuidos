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

QUEUE_SELECTQ2345_FILTERGENDER = "selectq2345_filterGender"
QUEUE_FILTERGENDER_FILTERDECADE = "filterGender_filterDecade"

QUEUE_FILTERGENDER_SELECTIDNAME_INDIE = "filterGender_selectIDNameIndie"
QUEUE_FILTERGENDER_SELECTIDNAME_ACTION = "filterGender_selectIDNameAction"

EXCHANGE_EOF_FILTERGENDER = "Exchange_filterGender"


class FilterGender:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.id = os.getenv("NODE_ID")
        self.total_nodes = int(os.getenv("TOTAL_NODES"))
        self.broker = Broker()
        self.games_indie = 0
        signal.signal(signal.SIGTERM, handler_sigterm_default(self.broker))
        self.broker.create_queue(name =QUEUE_SELECTQ2345_FILTERGENDER, callback = self.handler_filter_by_a_gender())
        self.broker.create_queue(name =QUEUE_FILTERGENDER_FILTERDECADE)
        self.broker.create_queue(name =QUEUE_FILTERGENDER_SELECTIDNAME_INDIE)
        self.broker.create_queue(name =QUEUE_FILTERGENDER_SELECTIDNAME_ACTION)

        self.handler_eof_games = HandlerEOF(broker =self.broker, node_id =self.id, target_name ="Games", total_nodes= self.total_nodes,
                            exchange_name =EXCHANGE_EOF_FILTERGENDER,
                            next_queues =[QUEUE_FILTERGENDER_FILTERDECADE, QUEUE_FILTERGENDER_SELECTIDNAME_INDIE])
        self.broker.create_fanout_and_bind(name_exchange =EXCHANGE_EOF_FILTERGENDER, callback =eof_calculator(self.handler_eof_games))

    def handler_filter_by_a_gender(self):
        def handler_message(ch, method, properties, body):
            result_dto = DetectDTO(body).get_dto()
            if result_dto.operation_type == OperationType.OPERATION_TYPE_EOF_DTO:
                self.handler_eof_games.init_leader_and_push_eof(result_dto)
            else:
                self.filter_for_gender(result_dto)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_message
    
    def get_gamesDTO_for_gender(self, batch_game, a_gender):
        some_games = []
        for game in batch_game.games_dto:
            if a_gender in game.genres.lower():
                if (a_gender == 'indie'):
                    self.games_indie += 1
                some_games.append(GameDTO(app_id =game.app_id, name =game.name,  release_date =game.release_date,
                                avg_playtime_forever =game.avg_playtime_forever))
        games_dto = GamesDTO(client_id =batch_game.client_id, state_games =StateGame.STATE_GENDER.value, games_dto =some_games)
        return games_dto

    def filter_for_gender(self, batch_game):
        indie_gamesDTO = self.get_gamesDTO_for_gender(batch_game, 'indie')
        actions_gamesDTO = self.get_gamesDTO_for_gender(batch_game, 'action')
        
        self.broker.public_message(queue_name =QUEUE_FILTERGENDER_FILTERDECADE, message =indie_gamesDTO.serialize())
        self.broker.public_message(queue_name =QUEUE_FILTERGENDER_SELECTIDNAME_INDIE, message =indie_gamesDTO.serialize())
        self.broker.public_message(queue_name =QUEUE_FILTERGENDER_SELECTIDNAME_ACTION, message =actions_gamesDTO.serialize())

        self.handler_eof_games.add_new_processing()


    def run(self):
        self.broker.start_consuming()
