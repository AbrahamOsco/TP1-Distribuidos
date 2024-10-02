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
        self.game_indexes = {}
        self.review_indexes = {}
        self.game_index_init= False
        self.review_index_init= False
        self.broker = Broker()
        self.broker.create_queue(name ='gateway_filterbasic', durable = True, callback =self.handler_callback())
        self.broker.create_exchange(name ="filter_basic", exchange_type='direct')
        self.wait_for_select = False

    def handler_callback(self):
        def handler_message(ch, method, properties, body):
            result = self.broker.get_message(body)
            for data_raw in result.data_raw:
                logging.info(f" 🍎 🗡️ 🍍 DATA-RAW  in filterbasic {data_raw}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_message
    

    def run(self):
        logging.info(f"In Filter basic!! 🧷 🧅")
        self.broker.start_consuming()
        logging.info(f"Filter basic started consuming!! 🧷 🚰")
    
    