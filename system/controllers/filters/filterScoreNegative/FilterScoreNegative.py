from common.utils.utils import initialize_log
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO
from system.commonsSystem.DTO.ReviewDTO import ReviewDTO
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.handlerEOF.HandlerEOF import HandlerEOF
from system.commonsSystem.utils.utils import eof_calculator, handler_sigterm_default
import logging
import os
import signal

EXCHANGE_EOF_SCORENEGATIVE = "Exchange_filterScoreNegative"
QUEUE_FILTERBASIC_SCORENEGATIVE = "filterBasic_scoreNegative"
QUEUE_SCORENEGATIVE_MONITORSTORAGEQ4 = "scoreNegative_monitorStorageQ4"

SCORE_NEGATIVE = -1

class FilterScoreNegative:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.id = os.getenv("NODE_ID")
        self.total_nodes = int(os.getenv("TOTAL_NODES"))

        self.broker = Broker()
        signal.signal(signal.SIGTERM, handler_sigterm_default(self.broker))
        self.broker.create_queue(name =QUEUE_FILTERBASIC_SCORENEGATIVE, callback = self.handler_filter_by_score_negative())
        self.broker.create_queue(name =QUEUE_SCORENEGATIVE_MONITORSTORAGEQ4)

        self.handler_eof_reviews = HandlerEOF(broker =self.broker, node_id =self.id, target_name ="Reviews", total_nodes= self.total_nodes,
                            exchange_name =EXCHANGE_EOF_SCORENEGATIVE, next_queues =[QUEUE_SCORENEGATIVE_MONITORSTORAGEQ4]) # tambien agregar selectIDNAME
        self.broker.create_fanout_and_bind(name_exchange =EXCHANGE_EOF_SCORENEGATIVE, callback =eof_calculator(self.handler_eof_reviews))


    def handler_filter_by_score_negative(self):
        def handler_message(ch, method, properties, body):
            result_dto = DetectDTO(body).get_dto()
            if result_dto.operation_type == OperationType.OPERATION_TYPE_EOF_DTO:
                logging.info(f"PUSH EOF!  {result_dto} 🔥🔥 👔👔👔👔👔👔👔👔👔👔👔👔 🗡️🗡️🗡️ ")
                self.handler_eof_reviews.init_leader_and_push_eof(result_dto)
            else:
                self.filter_using_score_negative(result_dto)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_message
    
    def get_reviewsDTO_with_score_negative(self, batch_reviews):
        some_reviews = []
        for review in batch_reviews.reviews_dto:
            if review.score == SCORE_NEGATIVE:
                some_reviews.append(ReviewDTO(app_id =review.app_id))
        reviews_dto = ReviewsDTO(client_id=batch_reviews.client_id, reviews_dto =some_reviews)
        return reviews_dto

    def filter_using_score_negative(self, batch_review):
        reviews_dto = self.get_reviewsDTO_with_score_negative(batch_review)
        self.broker.public_message(queue_name =QUEUE_SCORENEGATIVE_MONITORSTORAGEQ4, message =reviews_dto.serialize())
        self.handler_eof_reviews.add_new_processing()

    def run(self):
        self.broker.start_consuming()

