from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.DetectDTO import DetectDTO
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

QUEUE_SELECTQ2345_FILTERGENDER = "selectq2345_filterGender"
QUEUE_FILTERGENDER_FILTERDECADE = "filterGender_filterDecade"

QUEUE_FILTERGENDER_SELECTIDNAME = "filterGender_selectIDName"

EXCHANGE_EOF_FILTERGENDER_INDIE = "Exchange_filterGenderIndie"
EXCHANGE_EOF_FILTERGENDER_INDIE_ACTION = "Exchange_filterGenderIndieAction"


class FilterGender:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.id = os.getenv("NODE_ID")
        self.total_nodes = int(os.getenv("TOTAL_NODES"))
        self.broker = Broker()
        signal.signal(signal.SIGTERM, handler_sigterm_default(self.broker))
        self.broker.create_queue(name =QUEUE_FILTERGENDER_FILTERDECADE)
        self.broker.create_queue(name =QUEUE_FILTERGENDER_SELECTIDNAME)
        
        self.handler_eof_indie = HandlerEOF(broker =self.broker, node_id =self.id, target_name ="Games", total_nodes= self.total_nodes,
                            exchange_name =EXCHANGE_EOF_FILTERGENDER_INDIE, next_queues =[QUEUE_FILTERGENDER_FILTERDECADE])
        self.broker.create_fanout_and_bind(name_exchange =EXCHANGE_EOF_FILTERGENDER_INDIE, callback =eof_calculator(self.handler_eof_indie))

        self.handle_eof_indie_action = HandlerEOF(broker =self.broker, node_id =self.id, target_name ="Games", total_nodes= self.total_nodes,
                            exchange_name =EXCHANGE_EOF_FILTERGENDER_INDIE_ACTION, next_queues =[QUEUE_FILTERGENDER_SELECTIDNAME])
        self.broker.create_fanout_and_bind(name_exchange =EXCHANGE_EOF_FILTERGENDER_INDIE_ACTION, callback =eof_calculator(self.handle_eof_indie_action))
        self.broker.create_queue(name =QUEUE_SELECTQ2345_FILTERGENDER, callback =self.handler_filter_gender())

    def handler_filter_gender(self):
        def handler_message(ch, method, properties, body):
            result_dto = DetectDTO(body).get_dto()
            if result_dto.operation_type == OperationType.OPERATION_TYPE_EOF_DTO:
                self.handler_eof_indie.init_leader_and_push_eof(result_dto)  
                self.handle_eof_indie_action.init_leader_and_push_eof(result_dto)  
            else:
                self.filter_for_gender(result_dto)
            ch.basic_ack(delivery_tag =method.delivery_tag)
        return handler_message

    def get_games_indie_action(self, batch_game):
        only_indie_games = []
        indie_and_action_games = []
        for game in batch_game.games_dto:
            game_genres = game.genres.lower().split(',')
            if "indie" in game_genres:
                indie_game_dto = GameDTO(app_id =game.app_id, name =game.name,  release_date =game.release_date,
                                avg_playtime_forever =game.avg_playtime_forever, genres =game.genres)
                only_indie_games.append(indie_game_dto)
                indie_and_action_games.append(indie_game_dto)
            if "action" in game_genres:
                action_game_dto = GameDTO(app_id =game.app_id, name =game.name,  release_date =game.release_date,
                                avg_playtime_forever =game.avg_playtime_forever, genres =game.genres)
                indie_and_action_games.append(action_game_dto)
        return only_indie_games, indie_and_action_games

    def filter_for_gender(self, batch_game):
        indie_games, indie_action_games = self.get_games_indie_action(batch_game)
        indie_gamesDTO = GamesDTO(client_id =batch_game.client_id, state_games =StateGame.STATE_GENDER.value, games_dto =indie_games)
        action_indie_gamesDTO = GamesDTO(client_id =batch_game.client_id, state_games =StateGame.STATE_GENDER.value, games_dto =indie_action_games)

        self.handler_eof_indie.add_data_process(len(batch_game.games_dto))
        self.handler_eof_indie.add_data_sent(len(indie_games))
        
        self.handle_eof_indie_action.add_data_process(len(batch_game.games_dto))
        self.handle_eof_indie_action.add_data_sent(len(indie_action_games))
        
        self.broker.public_message(queue_name =QUEUE_FILTERGENDER_FILTERDECADE, message =indie_gamesDTO.serialize())
        self.broker.public_message(queue_name =QUEUE_FILTERGENDER_SELECTIDNAME, message =action_indie_gamesDTO.serialize())
        

    def run(self):
        self.broker.start_consuming()
