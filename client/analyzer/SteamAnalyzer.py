import logging
from common.utils.utils import initialize_log 
import os
from client.fileReader.FileReader import FileReader
from common.DTO.GamesRawDTO import GamesRawDTO
from common.DTO.ReviewsRawDTO import ReviewsRawDTO
from common.socket.Socket import Socket
from client.protocol.ClientProtocol import ClientProtocol

class SteamAnalyzer:

    def __init__(self):
        self.initialize_config()
        self.game_reader = FileReader(file_name='games', batch_size=25)
        self.review_reader = FileReader(file_name='reviews', batch_size=2000)

    def initialize_config(self):
        self.config_params = {}
        self.config_params["id"] = int(os.getenv("NODE_ID"))
        self.config_params["log_level"] = os.getenv("LOGGING_LEVEL")
        self.config_params["hostname"] = os.getenv("HOSTNAME")
        initialize_log(self.config_params["log_level"])
    
    def connect_to_server(self):
        self.socket = Socket(self.config_params["hostname"], 12345) #always put the name of docker's service nos ahorra problemas 👈
        result, msg =  self.socket.connect()
        logging.info(f"action: connect 🏪 | result: {result} | msg: {msg} 👈 ")
        self.protocol = ClientProtocol(a_id =self.config_params['id'], socket =self.socket)

    def run(self):
        self.connect_to_server()
        while True:
            some_games = self.game_reader.get_next_batch()
            if(some_games == None):
                break
            self.protocol.send_data_raw(GamesRawDTO(client_id =self.config_params['id'], games_raw =some_games))
        logging.info("action: All The game 🕹️ batches were sent! | result: success ✅")

        self.protocol.send_eof()

        while True:
            some_reviews = self.review_reader.get_next_batch()
            if(some_reviews == None):
                break
            self.protocol.send_data_raw(ReviewsRawDTO(client_id =self.config_params['id'], reviews_raw =some_reviews))
        logging.info("action: All the reviews 📰 batches were sent! | result: success ✅")

        self.protocol.send_eof()

    def get_result_from_queries(self):
        resultQuerys = self.protocol.recv_string()

    def stop(self):
        self.socket.close()
        self.game_reader.close()
        self.review_reader.close()
        logging.info("action: socket_closed 🏪 | result: success ✅")