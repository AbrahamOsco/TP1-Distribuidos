import logging
import random
from common.utils.utils import initialize_log 
import os
import threading
from client.fileReader.FileReader import FileReader
from client.fileReader.QueriesResponses import QueriesResponses
from common.DTO.GamesRawDTO import GamesRawDTO
from common.DTO.ReviewsRawDTO import ReviewsRawDTO
from common.socket.Socket import Socket
from client.protocol.ClientProtocol import ClientProtocol

class SteamAnalyzer:

    def __init__(self):
        self.initialize_config()
        percent_of_file_for_use = self.get_percent_of_file_for_use()
        logging.info(f"percent_of_file_for_use: {percent_of_file_for_use} 👈")
        self.game_reader = FileReader(file_name='games', batch_size=25, percent_of_file_for_use=percent_of_file_for_use)
        self.review_reader = FileReader(file_name='reviews', batch_size=2000, percent_of_file_for_use=percent_of_file_for_use)
        self.should_send_reviews = int(os.getenv("SEND_REVIEWS", 1)) == 1
        self.expected_responses = QueriesResponses(percent_of_file_for_use)
        self.actual_responses = {}
        self.threads = []

    def get_percent_of_file_for_use(self):
        valores = [0.1, 0.2, 0.3, 0.4, 0.5]
        return random.choice(valores)

    def initialize_config(self):
        self.config_params = {}
        self.config_params["id"] = int(os.getenv("NODE_ID"))
        self.config_params["log_level"] = os.getenv("LOGGING_LEVEL")
        self.config_params["hostname"] = os.getenv("HOSTNAME")
        initialize_log(self.config_params["log_level"])
    
    def connect_to_server(self):
        self.socket = Socket(self.config_params["hostname"], 12345)
        result, msg =  self.socket.connect()
        logging.info(f"action: connect 🏪 | result: {result} | msg: {msg} 👈 ")
        self.protocol = ClientProtocol(a_id =self.config_params['id'], socket =self.socket)

    def send_games(self):
        while True:
            some_games = self.game_reader.get_next_batch()
            if(some_games == None):
                break
            self.protocol.send_data_raw(GamesRawDTO(games_raw =some_games))
        logging.info("action: All The game 🕹️ batches were sent! | result: success ✅")
        self.protocol.send_games_eof(self.game_reader.get_lines_read())

    def send_reviews(self):
        if not self.should_send_reviews:
            return
        while True:
            some_reviews = self.review_reader.get_next_batch()
            if(some_reviews == None):
                break
            self.protocol.send_data_raw(ReviewsRawDTO(reviews_raw =some_reviews))
        logging.info("action: All the reviews 📰 batches were sent! | result: success ✅")
        self.protocol.send_reviews_eof(self.review_reader.get_lines_read())

    def send_data(self):
        self.send_games()
        self.send_reviews()

    def run(self):
        self.connect_to_server()
        self.threads.append(threading.Thread(target=self.send_data))
        self.threads.append(threading.Thread(target=self.get_result_from_queries))
        for thread in self.threads:
            thread.start()
        for thread in self.threads:
            thread.join()

    def get_result_from_queries(self):
        logging.info("action: Waiting for the results 📊 | result: pending ⌚")
        while True:
            resultQuerys = self.protocol.recv_result()
            if resultQuerys == None:
                break
            logging.info(f"action: result_received 📊 | result: success ✅")
            self.actual_responses = resultQuerys.append_data(self.actual_responses)
        logging.info("action: All the results 📊 were received! ✅")
        diff = self.expected_responses.diff(self.actual_responses)
        for query in diff:
            logging.info(f"action: diff | query: {query} | diff: {diff[query]}")

    def stop(self):
        self.socket.close()
        self.game_reader.close()
        self.review_reader.close()
        for thread in self.threads:
            thread.join()
        logging.info("action: socket_closed 🏪 | result: success ✅")