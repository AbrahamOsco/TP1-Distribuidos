from common.utils.utils import initialize_log
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from common.utils.utils import ALL_GAMES_WAS_SENT, ALL_REVIEWS_WAS_SENT
from system.commonsSystem.handlerEOF.HandlerEOF import HandlerEOF
from system.commonsSystem.utils.utils import eof_calculator, handler_sigterm_default
from system.commonsSystem.DTO.ResultQueryDTO import ResultQueryDTO, RESULT_WIHT_SIZE
import logging
import os
import signal

QUEUE_SCORENEGATIVE_MONITORSTORAGEQ5 = "scoreNegative_monitorStorageQ5"
QUEUE_SELECTIDNAME_MONITORSTORAGEQ5 = "selectIDName_monitorStorageQ5"
QUEUE_MONITORSTORAGEQ5_GROUPERPERCENTIL = "monitorStorageQ5_grouperPercentil"

BATCH_DIC_SIZE = 1

class MonitorStorageQ5:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.id = os.getenv("NODE_ID")
        self.games = {}
        self.broker = Broker()
        self.eof_games = None
        self.eof_reviews = None
        signal.signal(signal.SIGTERM, handler_sigterm_default(self.broker))
        self.broker.create_queue(name =QUEUE_SELECTIDNAME_MONITORSTORAGEQ5, callback = self.handler_insert_data_monitor())
        self.broker.create_queue(name =QUEUE_MONITORSTORAGEQ5_GROUPERPERCENTIL)

    def handler_insert_data_monitor(self):
        def handler_message(ch, method, properties, body):
            result_dto = DetectDTO(body).get_dto()
            if result_dto.operation_type == OperationType.OPERATION_TYPE_EOF_DTO and result_dto.old_operation_type == ALL_GAMES_WAS_SENT:
                self.eof_games = result_dto
                self.broker.create_queue(name =QUEUE_SCORENEGATIVE_MONITORSTORAGEQ5, callback = self.handler_insert_data_monitor()) # Creo recien la queue here
            elif result_dto.operation_type == OperationType.OPERATION_TYPE_EOF_DTO and result_dto.old_operation_type == ALL_REVIEWS_WAS_SENT:
                self.eof_reviews = result_dto
                self.send_batches_results() 
                self.broker.public_message(queue_name =QUEUE_MONITORSTORAGEQ5_GROUPERPERCENTIL, message =self.eof_reviews.serialize())
            else:
                self.udpate_storage_with_dto(result_dto)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_message

    def get_next_batch_of_game(self):
        some_games = {}
        some_app_ids = list(self.games.keys())[:BATCH_DIC_SIZE]
        for app_id in some_app_ids:
           some_games[app_id] = self.games[app_id]
           del self.games[app_id]
        return some_games
    
    def apply_filters_review_greater_zero(self):
        self.games = dict(filter(lambda item: item[1][1] > 0, self.games.items()))

    def send_batches_results(self):
        self.apply_filters_review_greater_zero()
        size_total_games = len(self.games)
        logging.info(f"Size resultant del dic luego del filtro {len(self.games)} 🤯 🔥 🎲🎲🎲🎲🎲")
        while len(self.games) > 0:
            batch_games = self.get_next_batch_of_game()
            monitor_resultDTO = ResultQueryDTO(client_id =self.eof_reviews.client_id, data =batch_games, status =RESULT_WIHT_SIZE, size_games = size_total_games)
            self.broker.public_message(queue_name =QUEUE_MONITORSTORAGEQ5_GROUPERPERCENTIL, message =monitor_resultDTO.serialize())


    def udpate_storage_with_dto(self, batch_data):
        if batch_data.operation_type == OperationType.OPERATION_TYPE_GAMES_DTO:
            for a_game in batch_data.games_dto:
                self.games[a_game.app_id] = [a_game.name, 0] 
        elif batch_data.operation_type == OperationType.OPERATION_TYPE_REVIEWS_DTO and self.eof_games:
            for a_review in batch_data.reviews_dto:
                if a_review.app_id in self.games.keys():
                    self.games[a_review.app_id][1] += 1
        
    def run(self):
        self.broker.start_consuming()
