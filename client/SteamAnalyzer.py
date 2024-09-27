import logging
from client.FileReader import FileReader
from common.socket.Socket import Socket
from client.ClientProtocol import ClientProtocol

class SteamAnalyzer:
    def __init__(self):
        self.initialize_log()
        self.game_reader = FileReader(file_name='games', batch_size=2)
        self.review_reader = FileReader(file_name='reviews', batch_size=2)
        self.socket = Socket("system", 12345) #siempre poner el nombre del service q esta en el docker compose nos ahorra problemas 👈
        result, msg =  self.socket.connect()
        logging.info(f"action: connect | result: {result} | msg: {msg} 👈 ")
        self.protocol = ClientProtocol(self.socket)
        self.run()

    def initialize_log(self, logging_level= logging.INFO):
        logging.basicConfig(
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=logging_level,
            datefmt='%Y-%m-%d %H:%M:%S',
        )

    def run(self):
        logging.info("action: The game batches send begins | result: success | 🍄 💯")
        for i in range(3):
            some_games = self.game_reader.get_next_batch()
            logging.info(f"action: some games are sent | result: sucess 🔥 | games: {some_games}")
            self.protocol.send_data_raw(some_games)
        
        logging.info("action: The reviews batches send begins | result: success | 📰 💯")
        for j in range(3):
            some_reviews = self.review_reader.get_next_batch()
            logging.info(f"action: review are sent | result: sucess 🔥 | games: {some_reviews}")

            self.protocol.send_data_raw(some_reviews)

    def get_result_from_queries(self):
        resultQuerys = self.protocol.recv_string()

    