import logging
import os
from client.FileReader import FileReader
from common.socket.Socket import Socket
from client.ClientProtocol import ClientProtocol, OPERATION_GAME_RAW, OPERATION_REVIEW_RAW

class SteamAnalyzer:
    def __init__(self):
        self.initialize_config()
        self.game_reader = FileReader(file_name='games', batch_size=2)
        self.review_reader = FileReader(file_name='reviews', batch_size=2)
        self.socket = Socket("system", 12345) #siempre poner el nombre del service q esta en el docker compose nos ahorra problemas 👈
        result, msg =  self.socket.connect()
        logging.info(f"action: connect | result: {result} | msg: {msg} 👈 ")
        self.protocol = ClientProtocol(a_id =self.config_params['id'], socket =self.socket)
        self.run()

    def initialize_config(self):
        self.config_params = {}
        self.config_params["id"] = int(os.getenv("CLI_ID"))
        self.config_params["log_level"] = os.getenv("CLI_LOG_LEVEL")
        self.initialize_log()


    def initialize_log(self):
        logging.basicConfig(
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=self.config_params["log_level"],
            datefmt='%Y-%m-%d %H:%M:%S',
        )

    def run(self):
        logging.info("action: The game batches send begins | result: success | 🍄 💯")
        for i in range(3):
            some_games = self.game_reader.get_next_batch()
            logging.info(f"action: some games are sent | result: sucess 🔥 | games: {some_games}")
            self.protocol.send_data_raw(OPERATION_GAME_RAW, some_games)
        
        logging.info("action: The reviews batches send begins | result: success | 📰 💯")
        for j in range(3):
            some_reviews = self.review_reader.get_next_batch()
            logging.info(f"action: review are sent | result: sucess 🔥 | games: {some_reviews}")
            self.protocol.send_data_raw(OPERATION_REVIEW_RAW, some_reviews)

    def get_result_from_queries(self):
        resultQuerys = self.protocol.recv_string()

    