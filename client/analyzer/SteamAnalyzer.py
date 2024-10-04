from common.utils.utils import initialize_log, ALL_DATA_WAS_SENT
from client.fileReader.FileReader import FileReader
from common.DTO.GamesRawDTO import GamesRawDTO
from common.DTO.ReviewsRawDTO import ReviewsRawDTO
from common.socket.Socket import Socket
from client.protocol.ClientProtocol import ClientProtocol
from client.resultWriter.ResultWriter import ResultWriter
import logging
import csv
import os
import signal
import time

class SteamAnalyzer:

    def __init__(self):
        self.initialize_config()
        self.game_reader = FileReader(file_name='games', batch_size=5)
        self.review_reader = FileReader(file_name='reviews', batch_size=5)
        self.result_writer = ResultWriter()
        self.there_was_sigterm = False
        signal.signal(signal.SIGTERM, self.handler_sigterm)

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
        try:
            self.connect_to_server()
            self.send_games()
            self.send_reviews()
            self.protocol.send_number_1_byte(ALL_DATA_WAS_SENT)
            self.get_result_from_queries()
        except Exception as e:
            if self.there_was_sigterm == False:
                logging.error(f"action: Handling a error | result: error ❌ | error: {e}")
        finally:
            self.free_all_resource()
            logging.info("action: Release all resource | result: success ✅")

    def free_all_resource(self):
        self.socket.close()
        self.review_reader.close()
        self.game_reader.close()

    def handler_sigterm(self, signum, frame):
        logging.info(f"action:⚡ signal SIGTERM {signum} has been caught sending EOF | result: sucess ✅ ")
        self.there_was_sigterm = True
        self.free_all_resource()

    def send_games(self):
        i = 0
        while  not self.game_reader.read_all_data() and i < 3:
            some_games = self.game_reader.get_next_batch()
            if(some_games == None):
                break
            self.protocol.send_data_raw(GamesRawDTO(client_id =self.config_params['id'], games_raw =some_games))
            i += 1
        if self.game_reader.read_all_data():
            logging.info(f"action: 10% of games.csv 🕹️ has been sent in batches | result: success ✅")

    def send_reviews(self):
        i = 0
        time.sleep(8)
        while not self.review_reader.read_all_data() and i < 3:
            some_reviews = self.review_reader.get_next_batch()
            if(some_reviews == None):
                break
            self.protocol.send_data_raw(ReviewsRawDTO(client_id =self.config_params['id'], reviews_raw =some_reviews))
            i += 1
        if self.review_reader.read_all_data():
            logging.info(f"action: 10% of review.csv  📰 🗞️ has been sent in batches! | result: success ✅")

    def get_result_from_queries(self):
        while True:
            logging.info("action: Waiting for results from queries | result: pending ⌚")
            result_query = self.protocol.recv_result_query()
            self.result_writer.run(result_query)



