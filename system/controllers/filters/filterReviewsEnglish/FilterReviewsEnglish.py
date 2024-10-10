from common.utils.utils import initialize_log
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO
from system.commonsSystem.DTO.ReviewDTO import ReviewDTO
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.handlerEOF.HandlerEOF import HandlerEOF
from system.commonsSystem.utils.utils import eof_calculator, handler_sigterm_default
from system.commonsSystem.DTO.ResultQueryDTO import ResultQueryDTO, RESULT_TOP

import langid
import logging
import os
import signal

QUEUE_MONITORSTORAGEQ4_FILTERENGLISH = "monitorStorageQ4_filterEnglish"
QUEUE_RESULTQ4_GATEWAY = "resultq4_gateway"
AMOUNT_NEED_REVIEWS_ENGLISH = 100

class FilterReviewsEnglish:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.id = os.getenv("NODE_ID")
        self.games ={}
        self.broker = Broker()
        signal.signal(signal.SIGTERM, handler_sigterm_default(self.broker))
        self.broker.create_queue(name =QUEUE_MONITORSTORAGEQ4_FILTERENGLISH, callback = self.handler_filter_by_amount_reviews_english())
        self.broker.create_queue(name =QUEUE_RESULTQ4_GATEWAY)

    def handler_filter_by_amount_reviews_english(self):
        def handler_message(ch, method, properties, body):
            result_dto = DetectDTO(body).get_dto()
            if result_dto.operation_type == OperationType.OPERATION_TYPE_EOF_DTO:
                result_queryDTO = ResultQueryDTO(client_id =result_dto.client_id, data =self.games, status =RESULT_TOP)
                self.broker.public_message(queue_name =QUEUE_RESULTQ4_GATEWAY, message =result_queryDTO.serialize() )
                logging.info(f"Respeustas QUERY4 IN Monitor {self.games} 🥉🥉🥉🥉🥉🥉🥉🥉🥉🥉🥉🥉🥉🥉🥉")
            else:
                self.filter_using_english(result_dto)
            ch.basic_ack(delivery_tag =method.delivery_tag)
        return handler_message
    
    def its_in_english(self, a_text_review):
        language, _ = langid.classify(a_text_review)
        return language == 'en'
    
    # batch_game_review.data tiene esta forma:  {123:["Dota2", ["a", "b", "c", ...] ], 4242: [ "AGE OF Emp2", ["good", "a", "b", "c"].]}
    # lo pasamos a {123:["Dota2", count_englihs_review], 4242: [ "AGE OF Emp2", 100]}
    def filter_using_english(self, batch_game_reviews):
        for app_id_game, nameGame_reviewList in batch_game_reviews.data.items():
            english_count = 0
            for review_text in nameGame_reviewList[1]:
                if self.its_in_english(review_text):
                    english_count += 1
            if english_count >= AMOUNT_NEED_REVIEWS_ENGLISH:
                self.games[app_id_game] = [nameGame_reviewList[0], english_count]
                logging.info(f"The game {nameGame_reviewList[0]} has {english_count} reviews in english")

    def run(self):
        self.broker.start_consuming()

