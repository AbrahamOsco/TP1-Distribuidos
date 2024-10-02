from common.utils.utils import initialize_log
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_GAMES_INITIAL
from system.commonsSystem.broker.Broker import Broker
import logging
import os
import time as t 

from system.commonsSystem.node.node import Node

class FilterBasic:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.game_indexes = {"AppID": 0 , "Name": 0, "Windows": 0, "Mac": 0, "Linux": 0,
                            "Genres": 0, "Release date": 0, "Average playtime forever": 0}
        self.review_indexes = { 'app_id':0, 'review_text':0, 'review_score':0 }
        self.game_index_init= False
        self.review_index_init= False
        self.broker = Broker()
        self.broker.create_exchange(name ="filter_basic", exchange_type='direct')
        self.wait_for_select = False
    
    def run(self):
        logging.info(f"In Filter basic!! 🧷 🧅")
        self.broker.start_consuming()
        logging.info(f"Filter basic started consuming!! 🧷 🚰")