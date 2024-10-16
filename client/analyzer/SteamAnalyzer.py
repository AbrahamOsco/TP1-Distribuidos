from common.utils.utils import initialize_log, ALL_GAMES_WAS_SENT, ALL_REVIEWS_WAS_SENT
from client.fileReader.FileReader import FileReader
from common.DTO.GamesRawDTO import GamesRawDTO
from common.DTO.ReviewsRawDTO import ReviewsRawDTO
from common.socket.Socket import Socket
from client.protocol.ClientProtocol import ClientProtocol
from client.resultWriter.ResultWriter import ResultWriter
from client.analyzer.CompareResults import CompareResults
import logging
import csv
import os
import signal
import time
import traceback
import threading
AMOUNT_BATCH_TO_SEND = 100000000
BATCH_SIZE = 1000
TOTAL_QUERYS = 5

class SteamAnalyzer:

    def __init__(self):
        self.initialize_config()
        self.game_reader = FileReader(file_name ='games', batch_size =BATCH_SIZE,
                            percent_of_file_for_use =self.config_params["percent_of_file"] )
        self.review_reader = FileReader(file_name ='reviews', batch_size =BATCH_SIZE,
                            percent_of_file_for_use =self.config_params["percent_of_file"])
        self.result_writer = ResultWriter()
        self.there_was_sigterm = False
        self.compare_results = CompareResults(self.config_params["percent_of_file"])
        self.results_obtained = 0
        signal.signal(signal.SIGTERM, self.handler_sigterm)
        self.thread_sender = threading.Thread(target=self.send_data_run)
    
    def initialize_config(self):
        self.config_params = {}
        self.config_params["percent_of_file"] = float(os.getenv("PERCENT_OF_FILE_FOR_USE"))
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
        #try:
            self.connect_to_server()
            self.thread_sender.start()
            self.get_result_from_queries()
        #except Exception as e:
        #    if self.there_was_sigterm == False:
        #        logging.error(f"action: Handling a error | error: ❌ {e} | result: sucess ✅")
        #finally:
            self.free_all_resource()
            logging.info("action: Release all resource | result: success ✅")

    def free_all_resource(self):
        self.socket.close()
        self.review_reader.close()
        self.game_reader.close()
        if self.thread_sender:
            self.thread_sender.join()

    def handler_sigterm(self, signum, frame):
        logging.info(f"action:⚡signal SIGTERM {signum} was received | result: sucess ✅ ")
        self.there_was_sigterm = True
        self.free_all_resource()

    def send_data_run(self):
        self.send_games()
        self.send_reviews()

    def send_games(self):
        while  not self.game_reader.read_all_data():
            some_games = self.game_reader.get_next_batch()
            if(some_games == None):
                break
            self.protocol.send_data_raw(GamesRawDTO(client_id =self.config_params['id'], games_raw =some_games))
        self.protocol.send_eof(ALL_GAMES_WAS_SENT, self.config_params['id'])
        if self.game_reader.read_all_data():
            logging.info(f"action: 10% of games.csv 🕹️ has been sent in batches Amount_data{self.game_reader.amount_data} | result: success ✅")

    def send_reviews(self):
        while not self.review_reader.read_all_data():
            some_reviews = self.review_reader.get_next_batch()
            if(some_reviews == None):
                break
            self.protocol.send_data_raw(ReviewsRawDTO(client_id =self.config_params['id'], reviews_raw =some_reviews))
        self.protocol.send_eof(ALL_REVIEWS_WAS_SENT, self.config_params['id'])
        if self.review_reader.read_all_data():
            logging.info(f"action: 10% of review.csv  📰 🗞️ has been sent in batches! Amount_data{self.review_reader.amount_data} | result: success ✅")

    def get_result_from_queries(self):
        while self.results_obtained < TOTAL_QUERYS :
            logging.info("action: Waiting for results from queries | result: pending ⌚")
            result_query = self.protocol.recv_result_query()
            self.result_writer.run(result_query)
            self.results_obtained +=1
        self.compare_results.compare()



