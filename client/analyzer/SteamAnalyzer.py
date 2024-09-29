import logging
from common.utils.utils import initialize_log 
import os
from client.fileReader.FileReader import FileReader
from common.socket.Socket import Socket
from client.protocol.ClientProtocol import ClientProtocol, OPERATION_GAME_RAW, OPERATION_REVIEW_RAW

class SteamAnalyzer:

    def __init__(self):
        self.initialize_config()
        self.game_reader = FileReader(file_name='games', batch_size=3)
        self.review_reader = FileReader(file_name='reviews', batch_size=3)
        self.run()

    def initialize_config(self):
        self.config_params = {}
        self.config_params["id"] = int(os.getenv("CLI_ID"))
        self.config_params["log_level"] = os.getenv("CLI_LOG_LEVEL")
        initialize_log(self.config_params["log_level"])
    
    def connect_to_server(self):
        self.socket = Socket("input", 12345) #always put the name of docker's service nos ahorra problemas 👈
        result, msg =  self.socket.connect()
        logging.info(f"action: connect | result: {result} | msg: {msg} 👈 ")
        self.protocol = ClientProtocol(a_id =self.config_params['id'], socket =self.socket)

    def run(self):
        self.connect_to_server()
        logging.info("action: The game batches send begins | result: success | 🍄 💯")
        for i in range(3):
            some_games = self.game_reader.get_next_batch()
            logging.info(f"action: a batch of game was sent! | result: sucess 🎮 | amount of games: {len(some_games)}")
            self.protocol.send_data_raw(OPERATION_GAME_RAW, some_games)
        logging.info("action: The reviews batches send begins | result: success | 📰 💯")
        for j in range(3):
            some_reviews = self.review_reader.get_next_batch()
            logging.info(f"action: a batch of review was sent! | result: sucess 💌 | amount of reviews: {len(some_reviews)}")
            self.protocol.send_data_raw(OPERATION_REVIEW_RAW, some_reviews)

    def get_result_from_queries(self):
        resultQuerys = self.protocol.recv_string()

