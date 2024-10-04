import logging
from enum import Enum

ALL_GAMES_WAS_SENT = 20
ALL_REVIEWS_WAS_SENT = 30

ALL_DATA_WAS_SENT = 10


DIC_GAME_FEATURES_TO_USE = {"AppID": 0 , "Name": 0, "Windows": 0, "Mac": 0, "Linux": 0,
                            "Genres": 0, "Release date": 0, "Average playtime forever": 0}
DIC_REVIEW_FEATURES_TO_USE = { 'app_id':0, 'review_text':0, 'review_score':0 }                              

class ResultType(Enum):
    RESULT_QUERY_1 = 1
    RESULT_QUERY_2 = 2
    RESULT_QUERY_3 = 3
    RESULT_QUERY_4 = 4
    RESULT_QUERY_5 = 5

def initialize_log(logging_level):
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging_level,
        datefmt='%Y-%m-%d %H:%M:%S',
    )

