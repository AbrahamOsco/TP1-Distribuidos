from common.utils.utils import initialize_log
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO
from system.commonsSystem.DTO.ReviewDTO import ReviewDTO
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.handlerEOF.HandlerEOF import HandlerEOF
from system.commonsSystem.utils.utils import eof_calculator, handler_sigterm_default
import langid
import logging
import os
import signal

QUEUE_MONITORSTORAGEQ4_FILTERENGLISH = "monitorStorageQ4_filterEnglish"
QUEUE_RESULTQ4_GATEWAY = "resultq4_gateway"
AMOUNT_NEED_REVIEWS_ENGLISH = 5000

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
                logging.info(f"PUSH EOF! Enviamos al gateway todo! ⚡⚡⚡⚡⚡⚡⚡ 👂👂👂👂? 💯💯💯 old_operation_type: 😮‍💨{result_dto.old_operation_type}")
            else:
                self.filter_using_english(result_dto)
            ch.basic_ack(delivery_tag =method.delivery_tag)
        return handler_message
    
    def detect_language(self, a_text):
        language, _ = langid.classify(a_text)
        return language

    def filter_using_english(self, batch_games_with_reviews):
        for key, value in batch_games_with_reviews.data.items():
            logging.info(f"Key: {key} Value {value} 🔥🔥🔥🔥🔥🔥🔥") 


    def run(self):
        self.broker.start_consuming()

