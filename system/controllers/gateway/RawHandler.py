import logging
from common.utils.utils import initialize_log, ALL_GAMES_WAS_SENT, ALL_REVIEWS_WAS_SENT
from system.commonsSystem.utils.utils import DIC_GAME_FEATURES_TO_USE, DIC_REVIEW_FEATURES_TO_USE
from common.DTO.GamesRawDTO import GamesRawDTO, OPERATION_TYPE_GAMES_RAW
from common.DTO.ReviewsRawDTO import ReviewsRawDTO, OPERATION_TYPE_REVIEWS_RAW
from system.commonsSystem.DTO.GamesIndexDTO import GamesIndexDTO
from system.commonsSystem.DTO.ReviewsIndexDTO import ReviewsIndexDTO

QUEUE_GATEWAY_FILTER = "gateway_filterBasic"

class RawHandler:
    def __init__(self, broker):
        self.game_indexes = DIC_GAME_FEATURES_TO_USE
        self.review_indexes = DIC_REVIEW_FEATURES_TO_USE
        self.all_client_data_was_recv = False
        self.game_index_init= False
        self.batchs_games = 0
        self.batchs_reviews = 0
        self.review_index_init= False
        self.there_was_sigterm =False
        self.broker = broker
        self.broker.create_queue(name =QUEUE_GATEWAY_FILTER)

    def handler_messages(self, raw_dto):
        if raw_dto.operation_type == ALL_GAMES_WAS_SENT:
            raw_dto.initialize_amount_and_type(self.batchs_games)
            self.broker.public_message(queue_name =QUEUE_GATEWAY_FILTER, message = raw_dto.serialize())
            logging.info(f"action: Sent EOF of Games 🕹️! ⭐ | result: success ✅")
        elif raw_dto.operation_type == ALL_REVIEWS_WAS_SENT:
            self.all_client_data_was_recv = True
            raw_dto.initialize_amount_and_type(self.batchs_reviews)
            self.broker.public_message(queue_name =QUEUE_GATEWAY_FILTER, message = raw_dto.serialize())
            logging.info(f"action: Sent EOF of Reviews 📰!  | result: sucess ✅")
        else:
             self.handler_games_and_reviews(raw_dto)

    def handler_games_and_reviews(self, raw_dto):
        self.initialize_indexes(raw_dto.operation_type, raw_dto.data_raw)
        a_index_dto = None
        if raw_dto.operation_type == OPERATION_TYPE_GAMES_RAW:
            self.batchs_games +=1
            a_index_dto = GamesIndexDTO(client_id =raw_dto.client_id,
                                        games_raw =raw_dto.data_raw, indexes = self.game_indexes)
        elif raw_dto.operation_type == OPERATION_TYPE_REVIEWS_RAW:
            self.batchs_reviews +=1
            a_index_dto = ReviewsIndexDTO(client_id =raw_dto.client_id,
                                            reviews_raw =raw_dto.data_raw, indexes =self.review_indexes)
        self.broker.public_message(queue_name =QUEUE_GATEWAY_FILTER, message = a_index_dto.serialize())
        
    def initialize_indexes(self, operation_type, list_items):
        if operation_type == OPERATION_TYPE_GAMES_RAW and self.game_index_init == True:
            return
        elif operation_type == OPERATION_TYPE_REVIEWS_RAW and self.review_index_init == True:
            return
        elif self.game_index_init == False:
            self.find_main_index(list_items, self.game_indexes, self.game_index_init)
            self.game_index_init = True
        elif self.review_index_init == False:
            self.find_main_index(list_items, self.review_indexes, self.review_index_init)
            self.review_index_init = True
    
    def find_main_index(self, list_items, dic_index, index_init):
        for i, element in enumerate(list_items[0]):
                if element in dic_index.keys():
                    dic_index[element] = i
        list_items.pop(0)

    def run(self, protocol):
        while not self.all_client_data_was_recv and not self.there_was_sigterm:
            self.handler_messages(protocol.recv_data_raw())

    def close(self):
        self.there_was_sigterm = True

    