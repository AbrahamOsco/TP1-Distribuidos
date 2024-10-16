from common.utils.utils import initialize_log, ALL_GAMES_WAS_SENT, ALL_REVIEWS_WAS_SENT
from common.DTO.GamesRawDTO import GamesRawDTO, OPERATION_TYPE_GAMES_RAW
from common.DTO.ReviewsRawDTO import ReviewsRawDTO, OPERATION_TYPE_REVIEWS_RAW
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.DTO.enums.StateGame import StateGame
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO
import logging
import threading

QUEUE_GATEWAY_FILTER = "gateway_filterBasic"

class RawHandler:
    def __init__(self):
        self.all_client_data_was_recv = False
        self.amount_games = 0
        self.amount_reviews = 0
        self.broker = Broker()
        self.there_was_sigterm = False
        self.broker.create_queue(name =QUEUE_GATEWAY_FILTER)
        self.thread_receiver = None
        self.protocol = None

    def handler_messages(self, raw_dto):
        if raw_dto.operation_type == ALL_GAMES_WAS_SENT:
            raw_dto.initialize_amount_and_type(self.amount_games)
            self.broker.public_message(queue_name =QUEUE_GATEWAY_FILTER, message = raw_dto.serialize())
            logging.info(f"action: Sent EOF of Games 🕹️ ⭐ | result: success ✅")
        elif raw_dto.operation_type == ALL_REVIEWS_WAS_SENT:
            self.all_client_data_was_recv = True
            raw_dto.initialize_amount_and_type(self.amount_reviews)
            self.broker.public_message(queue_name =QUEUE_GATEWAY_FILTER, message = raw_dto.serialize())
            logging.info(f"action: Sent EOF of Reviews 📰 ⭐  | result: sucess ✅")
        else:
             self.handler_games_and_reviews(raw_dto)

    def handler_games_and_reviews(self, raw_dto):
        a_dto_to_send = None
        if raw_dto.operation_type == OPERATION_TYPE_GAMES_RAW:
            a_dto_to_send = GamesDTO(client_id=raw_dto.client_id, state_games = StateGame.STATE_GAMES_INITIAL.value, games_raw=raw_dto.data_raw)
            self.amount_games += len(raw_dto.data_raw)
        elif raw_dto.operation_type == OPERATION_TYPE_REVIEWS_RAW:
            self.amount_reviews += len(raw_dto.data_raw)
            a_dto_to_send = ReviewsDTO(client_id =raw_dto.client_id, reviews_raw =raw_dto.data_raw)
        self.broker.public_message(queue_name =QUEUE_GATEWAY_FILTER, message = a_dto_to_send.serialize())
        
    def run(self, protocol):
        self.protocol = protocol
        while not self.all_client_data_was_recv and not self.there_was_sigterm:
            self.handler_messages(self.protocol.recv_data_raw())
    
    def start(self, protocol):
        self.thread_receiver = threading.Thread(target=self.run, args=(protocol,))
        self.thread_receiver.start()

    def close(self):
        if self.thread_receiver:
            self.thread_receiver.join()
        self.there_was_sigterm = True

    