from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.RawDTO import RawDTO
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.node.routingPolicies.RoutingOneToOne import RoutingOneToOne

class Filter(Node):
    def __init__(self):
        super().__init__(RoutingOneToOne())
        self.game_indexes = {0:"app_id" , 1:"name", 2:"release_date", 17: "windows", 18: "mac", 19: "linux", 29: "avg_playtime_forever", 36: "genres"}
        self.review_indexes = {0:'app_id', 2:'review_text', 3:'review_score'}
    
    def send_reviews(self, data: RawDTO):
        reviews = ReviewsDTO.from_raw(data, self.review_indexes)
        if len(reviews.reviews_dto) == 0:
            return
        self.broker.public_message(sink=self.sink, message=reviews.serialize(), routing_key="reviews")

    def send_games(self, data: RawDTO):
        games = GamesDTO.from_raw(data, self.game_indexes)
        if len(games.games_dto) == 0:
            return
        self.broker.public_message(sink=self.sink, message=games.serialize(), routing_key="games")

    def process_data(self, data: RawDTO):
        if data.is_games():
            self.send_games(data)
        elif data.is_reviews():
            self.send_reviews(data)