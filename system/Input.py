from common.socket.Socket import Socket
from system.ServerProtocol import ServerProtocol, OPERATION_GAME_RAW, OPERATION_REVIEW_RAW
import logging

class Input:
    def __init__(self):
        self.initialize_log()
        self.socket_accepter = Socket(port =12345)
        logging.info("action: Waiting a client to connect result: pending ⌚")
        self.socket_peer, addr = self.socket_accepter.accept()
        logging.info("action: Waiting a client to connect result: success ✅")
        self.protocol = ServerProtocol(self.socket_peer)
        self.game_indexes = {"AppID": 0 , "Name": 0, "Windows": 0, "Mac": 0, "Linux": 0,\
            "Genres": 0, "Release date": 0, "Average playtime forever": 0}
        self.review_indexes = { 'app_id':0, 'review_text':0, 'review_score':0 }
        self.game_index_init= False
        self.review_index_init= False

    def run(self):
        logging.info("action: Input prepare to recv data! | 😶‍🌫️🍄")
        while True:
            id_client, operation_type, list_items = self.protocol.recv_data_raw()
            self.initialize_indexes(operation_type, list_items)
            batch_item_filtered = self.filter_fields_item(operation_type, list_items)
            logging.info(f"client_id: {id_client} operation: {operation_type} | item filtered: {batch_item_filtered}")
    
    def initialize_log(self, logging_level= logging.INFO):
        logging.basicConfig(
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=logging_level,
            datefmt='%Y-%m-%d %H:%M:%S',
        )

    # funcion para filtrar y luego codear un exchange con routing key= game q pushee a las queues games_q1 y games_q2345
    # y luego un mensaje con ruting_key=review q pushe a la queue reviwes_raw

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
        item_basic = []
        for i in range(len(a_item)):
            if i in dic_indexes.values():
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

    