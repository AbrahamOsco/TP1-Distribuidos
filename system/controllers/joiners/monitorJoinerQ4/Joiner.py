import logging
from system.commonsSystem.node.node import Node, UnfinishedGamesException, UnfinishedReviewsException
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO
from system.commonsSystem.DTO.GamesDTO import GamesDTO

STATUS_STARTED = 0
STATUS_REVIEWING = 1

class Joiner(Node):
    def __init__(self):
        super().__init__()
        self.reset_list()

    def reset_list(self):
        self.list = {}
        self.status = STATUS_STARTED

    def inform_eof_to_nodes(self, client):
        if self.status == STATUS_REVIEWING:
            self.update_totals(client, self.amount_received_by_node[client], self.amount_sent_by_node[client])     
            self.send_eof(client)
            self.reset_list()
            self.reset_amounts(client)
            self.status = STATUS_STARTED
            logging.info("Status changed. Now is expecting games")
        else:
            self.status = STATUS_REVIEWING
            self.amount_received_by_node[client] = 0
            self.amount_sent_by_node[client] = 0
            logging.info("Status changed. Now is expecting reviews")

    def send_review(self, data):
        self.broker.public_message(sink=self.sink, message=data.serialize(), routing_key="default")

    def process_reviews(self, data: ReviewsDTO):
        if self.status == STATUS_STARTED:
            raise UnfinishedGamesException()
        self.update_amount_received_by_node(data.get_client(), data.get_amount())
        data.filter_reviews(lambda review: review.app_id in self.list)
        if len(data.reviews_dto) > 0:
            data.apply_on_reviews(lambda review: review.set_name(self.list[review.app_id]))
            self.update_amount_sent_by_node(data.get_client(), data.get_amount())
            self.send_review(data)

    def process_games(self, data: GamesDTO):
        if self.status == STATUS_REVIEWING:
            raise UnfinishedReviewsException()
        self.update_amount_received_by_node(data.get_client(), data.get_amount())
        for game in data.games_dto:
            self.list[game.app_id] = game.name

        self.update_amount_sent_by_node(data.get_client(), data.get_amount())

    def process_data(self, data):
        if data.is_reviews():
            self.process_reviews(data)
        if data.is_games():
            self.process_games(data)