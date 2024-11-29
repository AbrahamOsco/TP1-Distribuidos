from common.utils.utils import initialize_log
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.DTO.EOFDTO import EOFDTO
from system.commonsSystem.DTO.BatchDTO import BatchDTO
from common.tolerance.IDList import IDList
from system.commonsSystem.node.structures.dualInputStructure import DualInputStructure, STATUS_STARTED, STATUS_REVIEWING
from system.commonsSystem.node.statefullNode import StatefullNode
import logging

class DualInputNode(StatefullNode):
    def __init__(self, counter_size):
        initialize_log(logging_level='INFO')
        self.review_id_list = IDList()
        self.games_id_list = IDList()
        self.data = DualInputStructure(counter_size)
        super().__init__(self.data, [self.review_id_list, self.games_id_list])

    def inform_eof_to_nodes(self, data, delivery_tag: str):
        client_id = data.get_client()
        if data.get_type() == "reviews" and self.data.status[client_id] == STATUS_REVIEWING:
            self.check_amounts(data)
            logging.info(f"Status changed for client {data.get_client()}. Finished.")
        elif data.get_type() == "games" and self.data.status[client_id] == STATUS_STARTED:
            self.data.status[client_id] = STATUS_REVIEWING
            self.check_amounts(data)
            logging.info(f"Status changed for client {data.get_client()}. Now is expecting reviews")
            self.checkpoint.save_checkpoint(self.data.to_bytes())
            self.check_premature_messages(data.get_client())
        self.broker.basic_ack(delivery_tag=0,multiple=True)

    def check_premature_messages(self, client_id):
        if len(self.data.premature_messages[client_id]) == 0:
            return
        for data in self.data.premature_messages[client_id]:
            self.process_reviews(data)
        self.checkpoint.save_checkpoint(self.data.to_bytes())

    def check_amounts(self, data: EOFDTO):
        if data.get_type() == "games":
            return
        client = data.get_client()
        self.send_result(client)
        self.send_eof(data)
        self.data.reset(client)
        self.checkpoint.save_checkpoint(self.data.to_bytes())
     
    def send_games(self, client_id, games, state, query=0):
        global_counter = self.data.counter[client_id].pop(0)
        gamesDTO = GamesDTO(client_id=client_id, state_games=state, games_dto=games, query=query, global_counter=global_counter)
        self.broker.public_message(sink=self.sink, message=gamesDTO.serialize(), routing_key="default")

    def send_result(self, client_id):
        pass

    def add_premature_message(self, data: ReviewsDTO):
        client_id = data.get_client()
        if client_id not in self.data.premature_messages:
            self.data.premature_messages[client_id] = []
        self.data.premature_messages[client_id].append(data)

    def process_reviews(self, data: ReviewsDTO):
        if self.review_id_list.already_processed(data.global_counter):
            logging.error(f"Review {data.global_counter} already processed")
            return

        client_id = data.get_client()
        if self.data.status[client_id] == STATUS_STARTED:
            logging.debug(f"Client {client_id} is still started")
            self.add_premature_message(data) # TODO: Revisar que onda con esto
            return
        self.review_id_list.insert(data.global_counter)
        for review in data.reviews_dto:
            if review.app_id in self.data.list[client_id]:
                self.data.list[client_id][review.app_id] += 1

    def process_games(self, data: GamesDTO):
        if self.games_id_list.already_processed(data.global_counter):
            logging.error(f"Game {data.global_counter} already processed")
            return
        # else:
        #     logging.info(f"Processing game {data.global_counter}")
        self.games_id_list.insert(data.global_counter)
        client_id = data.get_client()
        self.data.add_counter(client_id, data.global_counter)
        for game in data.games_dto:
            self.data.list[client_id][game.app_id] = 0
            self.data.games[client_id][game.app_id] = game.name

    def process_data(self, data: BatchDTO):
        client_id = data.get_client()
        self.data.init(client_id)
        self.logs.add_log(data.serialize())
        if data.is_reviews():
            self.process_reviews(data)
        if data.is_games():
            self.process_games(data)
        if self.logs.is_full():
            self.checkpoint.save_checkpoint(self.data.to_bytes())