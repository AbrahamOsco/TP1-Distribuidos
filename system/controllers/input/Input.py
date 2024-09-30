from common.utils.utils import initialize_log 
from common.socket.Socket import Socket
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_GAMES_INITIAL
from system.commonsSystem.broker.Broker import Broker
import logging
import os
import time as t 
from system.commonsSystem.protocol.ServerProtocol import ServerProtocol, OPERATION_GAME_RAW, OPERATION_REVIEW_RAW

class Input:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.game_indexes = {"AppID": 0 , "Name": 0, "Windows": 0, "Mac": 0, "Linux": 0,\
            "Genres": 0, "Release date": 0, "Average playtime forever": 0}
        self.review_indexes = { 'app_id':0, 'review_text':0, 'review_score':0 }
        self.game_index_init= False
        self.review_index_init= False
        self.broker = Broker()
        self.broker.create_exchange(name='games_reviews_input', exchange_type='direct')
        self.wait_for_select = False

    def accept_a_connection(self):
        self.socket_accepter = Socket(port =12345)
        logging.info("action: Waiting a client to connect result: pending ⌚")
        self.socket_peer, addr = self.socket_accepter.accept()
        logging.info("action: Waiting a client to connect result: success ✅")
        self.protocol = ServerProtocol(self.socket_peer)
    
    def run(self):
        self.accept_a_connection()
        logging.info("action: Input prepare to recv data! | 😶‍🌫️🍄")
        i = 0
        while True:
            client_id, operation_type, list_items = self.protocol.recv_data_raw()
            self.initialize_indexes(operation_type, list_items)
            batch_item_filtered = self.filter_fields_item(operation_type, list_items)
            logging.info(f"client_id: {client_id} operation: {operation_type} | item filtered: {batch_item_filtered}")
            if not self.wait_for_select:
                t.sleep(2)
                logging.info("action: Waiting for bind some queues to the exchange! | result: finish with success ✅")
                self.wait_for_select = True
            self.send_batch_data(batch_item_filtered, operation_type, client_id)
    
    # for each game se cumple:  ['AppID', 'Name', 'Release date', 'Windows', 'Mac', 'Linux', 'Average playtime forever', 'Genres']
    # example: ['1659180', 'TD Worlds', 'Jan 9, 2022', 'True', 'False', 'False', '0', 'Indie,Strategy']
    
    def send_batch_data(self, data_filtered, operation_type, client_id):
        if operation_type == OPERATION_GAME_RAW:
            game_dto = GamesDTO(games_raw =data_filtered, client_id =client_id, state_games =STATE_GAMES_INITIAL)
            self.broker.public_message(exchange_name='games_reviews_input', routing_key='games.q1', message = "Some data 🛡️ 👨‍🔧  〽️ 🐲")
            self.broker.public_message(exchange_name='games_reviews_input', routing_key='games.q2345', message = "Some data 🩹 🅰️ 🥑")
        elif operation_type == OPERATION_REVIEW_RAW:
            self.broker.public_message(exchange_name='games_reviews_input', routing_key='reviews.raw', message ="Some data 🛡️ 👨‍🔧 🗡️")

    def filter_fields_item(self, operation_type, list_items):
        batch_item = []
        if operation_type == OPERATION_GAME_RAW:
            for a_game in list_items:
                basic_game = self.drop_basic_item(a_game, self.game_indexes)
                batch_item.append(basic_game)
        elif operation_type == OPERATION_REVIEW_RAW:
            for a_review in list_items:
                basic_review = self.drop_basic_item(a_review, self.review_indexes)
                batch_item.append(basic_review)
        return batch_item

    def drop_basic_item(self, a_item, dic_indexes):
        logging.info(f"Dic Indexes 🦃 : {dic_indexes}")
        item_basic = []
        for i in range(len(a_item)):
            if i in dic_indexes.values():
                logging.info(f"index: {i} value: {a_item[i]}")
                item_basic.append(a_item[i])
        return item_basic

    def initialize_indexes(self, operation_type, list_items):
        if operation_type == OPERATION_GAME_RAW and self.game_index_init == True:
            return
        elif operation_type == OPERATION_REVIEW_RAW and self.review_index_init == True:
            return
        elif self.game_index_init == False:
            for i, element in enumerate(list_items[0]):
                if element in self.game_indexes.keys():
                    self.game_indexes[element] = i
            list_items.pop(0)
            self.game_index_init = True
        
        elif self.review_index_init == False:
            for i, element in enumerate(list_items[0]):
                if element in self.review_indexes.keys():
                    self.review_indexes[element] = i
            list_items.pop(0)
            self.review_index_init = True

    