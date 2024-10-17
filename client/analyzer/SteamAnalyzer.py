import logging
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
        self.actual_responses = {}
        self.threads = []
        self.socket = None
        self.protocol = None

    def init_readers_and_responses(self, percent_of_file):
        self.percent = percent_of_file
        self.game_reader = FileReader(file_name='games', batch_size=25, percent_of_file_for_use=self.percent)
        self.review_reader = FileReader(file_name='reviews', batch_size=2000, percent_of_file_for_use=self.percent)
        self.should_send_reviews = int(os.getenv("SEND_REVIEWS", 1)) == 1
        self.expected_responses = QueriesResponses(self.percent,os.getenv("QUERIES_EXECUTED"))

    def initialize_config(self):
        self.config_params = {}
        self.config_params["id"] = int(os.getenv("NODE_ID"))
        self.config_params["log_level"] = os.getenv("LOGGING_LEVEL")
        self.config_params["hostname"] = os.getenv("HOSTNAME")
        initialize_log(self.config_params["log_level"])
        self.percentages = []

    def connect_to_server(self):
        self.socket = Socket(self.config_params["hostname"], 12345) #always put the name of docker's service nos ahorra problemas 👈
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
        self.protocol.send_auth()
        self.send_games()
        self.send_reviews()

    def run(self):
        percent_of_file_for_use_by_execution = os.getenv("PERCENT_OF_FILE_FOR_USE_BY_EXECUTION", 1)
        self.percentages = [float(p.strip()) for p in percent_of_file_for_use_by_execution.split(',')]
        logging.info(f"Starting executions of Client")
        for i, percent in enumerate(self.percentages, 1):
            logging.info(f"Starting execution {i} of {len(self.percentages)} with {percent*100}% of file")
            self.execute(percent)
            logging.info(f"Finished execution {i} of {percent}")
        logging.info("All executions completed")
    
    def execute(self, percent):
        self.init_readers_and_responses(percent)
        self.connect_to_server()
        self.threads.append(threading.Thread(target =self.send_data))
        self.threads.append(threading.Thread(target =self.get_result_from_queries))
        for thread in self.threads:
            thread.start()
        for thread in self.threads:
            thread.join()
        self.stop()

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
        self.threads = []
        logging.info("action: Client stop! 🏪 | result: success ✅")