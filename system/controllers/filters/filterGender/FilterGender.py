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
QUEUE_FILTERGENDER_SELECTIDNAME = "filterGender_selectIDName"
EXCHANGE_EOF_FILTERGENDER = "Exchange_filterGender"


class FilterGender():
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.id = os.getenv("NODE_ID")
        self.total_nodes = int(os.getenv("TOTAL_NODES"))

        self.broker = Broker()
        signal.signal(signal.SIGTERM, handler_sigterm_default(self.broker))
        self.broker.create_queue(name =QUEUE_SELECTQ2345_FILTERGENDER, callback = self.filter_by_a_gender())
        self.broker.create_queue(name =QUEUE_FILTERGENDER_FILTERDECADE)

        self.handler_eof_games = HandlerEOF(broker =self.broker, node_id =self.id, target_name ="Games", total_nodes= self.total_nodes,
                            exchange_name =EXCHANGE_EOF_FILTERGENDER, next_queues =[QUEUE_FILTERGENDER_FILTERDECADE]) # tambien agregar selectIDNAME
        self.broker.create_fanout_and_bind(name_exchange =EXCHANGE_EOF_FILTERGENDER, callback =eof_calculator(self.handler_eof_games))

    def filter_by_a_gender(self):
        def handler_message(ch, method, properties, body):
            result_dto = DetectDTO(body).get_dto()
            if result_dto.operation_type == OperationType.OPERATION_TYPE_EOF_DTO:
                self.handler_eof_games.init_lider_and_push_eof(result_dto)
                logging.info(f"Action: Recv Game EOF ! 🪀🕹️🕹️: 🔥🔥🔥🔥🔥 | result: success ✅")
            else:
                self.filter_for_gender(result_dto)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_message
    
    def get_gamesDTO_for_gender(self, batch_game, a_gender):
        some_games = []
        for game in batch_game.games_dto:
            if a_gender in game.genres.lower():
                some_games.append(GameDTO(app_id =game.app_id, name =game.name,  release_date =game.release_date,
                                avg_playtime_forever =game.avg_playtime_forever))
        games_dto = GamesDTO(client_id =batch_game.client_id, state_games =StateGame.STATE_GENDER.value, games_dto =some_games)
        return games_dto

    def filter_for_gender(self, batch_game):
        indie_gamesDTO = self.get_gamesDTO_for_gender(batch_game, 'indie')
        actions_gamesDTO = self.get_gamesDTO_for_gender(batch_game, 'action')
        
        self.broker.public_message(queue_name =QUEUE_FILTERGENDER_FILTERDECADE, message =indie_gamesDTO.serialize())
        logging.info(f"action: Send Indie GamesDTO 🔥 🌟 to filter_decade | count: {len(indie_gamesDTO.games_dto)} | result: success ✅")
        self.handler_eof_games.add_new_processing()
        #self.broker.public_message(queue_name=QUEUE_FILTERGENDER_SELECTIDNAME, message=actions_gamesDTO.serialize())
        #logging.info(f"action: Send Action GamesDTO 🔫 ⚽ to select_id_name | count: {len(actions_gamesDTO.games_dto)} | result: success ✅")


    def run(self):
        self.broker.start_consuming()
