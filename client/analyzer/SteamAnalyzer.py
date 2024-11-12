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

CLIENT_ID_LOG_PATH = "/data/client_id.log"
INVALID_CLIENT_ID = 0
class SteamAnalyzer:

    def __init__(self):
        self.initialize_config()
        self.threads = []
        self.socket = None
        self.protocol = None
        self.batch_id = 1
        self.there_a_signal = False
        self.should_send_reviews = int(os.getenv("SEND_REVIEWS", 1)) == 1

    def init_readers_and_responses(self, percent_of_file):
        self.percent = percent_of_file
        self.actual_responses = {}
        self.game_reader = FileReader(file_name='games', batch_size=25, percent_of_file_for_use=self.percent)
        self.review_reader = FileReader(file_name='reviews', batch_size=2000, percent_of_file_for_use=self.percent)
        self.expected_responses = QueriesResponses(self.percent,os.getenv("QUERIES_EXECUTED"))

    def initialize_config(self):
        self.config_params = {}
        self.config_params["log_level"] = os.getenv("LOGGING_LEVEL")
        self.config_params["hostname"] = os.getenv("HOSTNAME")
        initialize_log(self.config_params["log_level"])
        self.config_params["id"] = self.get_client_id()
        self.percentages = []

    def get_client_id(self):
        if os.path.exists(CLIENT_ID_LOG_PATH):
            with open(CLIENT_ID_LOG_PATH, "r") as file:
                client_id = int(file.read().strip())
                logging.info(f"action: load_existing_id | client_id: {client_id}")
                return client_id
        logging.info(f"action: get_id_client | client_id: {None}")
        return None

    def connect_to_server(self):
        self.socket = Socket(self.config_params["hostname"], 12345) #always put the name of docker's service nos ahorra problemas 👈
        result, msg =  self.socket.connect()
        logging.info(f"action: connect 🏪 | result: {result} | msg: {msg} 👈 ")
        self.protocol = ClientProtocol(socket =self.socket)

    def send_games(self):
        logging.info("action: Sending Games | result: pending ⌚")
        while self.there_a_signal == False:
            some_games = self.game_reader.get_next_batch()
            if(some_games == None):
                break
            self.protocol.send_data_raw(GamesRawDTO(games_raw=some_games, batch_id=self.batch_id))
            self.batch_id += 1
        logging.info("action: All The game 🕹️ batches were sent! | result: success ✅")
        self.protocol.send_games_eof(self.batch_id)
        self.batch_id += 1

    def send_reviews(self):
        if not self.should_send_reviews:
            return
        logging.info("action: Sending Reviews | result: pending ⌚")
        while self.there_a_signal == False:
            some_reviews = self.review_reader.get_next_batch()
            if(some_reviews == None):
                break
            self.protocol.send_data_raw(ReviewsRawDTO(reviews_raw=some_reviews, batch_id=self.batch_id))
            self.batch_id += 1
        logging.info("action: All the reviews 📰 batches were sent! | result: success ✅")
        self.protocol.send_reviews_eof(self.batch_id)
        self.batch_id += 1

    def send_data(self):
        try:
            if (self.batch_id > 1):
                self.find_and_send_remaining_data()
            else:
                self.send_games()
                self.send_reviews()
        except Exception as e:
            logging.info(f"action: Error Catch from thread Sender: {e} | result: success ✅ ")

    def find_and_send_remaining_data(self):
        logging.info("action: Finding and sending remaining data | result: pending ⌚")
        local_batch_id = 1
        games_eof_sent = False
        reviews_eof_sent = False

        while not self.there_a_signal:
            some_games = self.game_reader.get_next_batch()
            if some_games is None:
                logging.info("action: No more game batches left to process.")
                break

            if local_batch_id <= self.batch_id:
                logging.info(f"action: Skipping game batch | local_batch_id: {local_batch_id}")
                local_batch_id += 1
                continue

            self.protocol.send_data_raw(GamesRawDTO(games_raw=some_games, batch_id=local_batch_id))
            logging.info(f"action: Sent game batch | batch_id: {local_batch_id} ✅")
            local_batch_id += 1

        if not games_eof_sent and not self.there_a_signal:
            self.protocol.send_games_eof(local_batch_id)
            logging.info(f"action: Sent games EOF | batch_id: {local_batch_id}")
            local_batch_id += 1
            games_eof_sent = True

        if self.should_send_reviews:
            logging.info("action: Resuming with reviews | result: pending ⌚")
            while not self.there_a_signal:
                some_reviews = self.review_reader.get_next_batch()
                if some_reviews is None:
                    logging.info("action: No more review batches left to process.")
                    break

                if local_batch_id <= self.batch_id:
                    logging.info(f"action: Skipping review batch | local_batch_id: {local_batch_id}")
                    local_batch_id += 1
                    continue

                self.protocol.send_data_raw(ReviewsRawDTO(reviews_raw=some_reviews, batch_id=local_batch_id))
                logging.info(f"action: Sent review batch | batch_id: {local_batch_id} ✅")
                local_batch_id += 1

            if not reviews_eof_sent and not self.there_a_signal:
                self.protocol.send_reviews_eof(local_batch_id)
                logging.info(f"action: Sent reviews EOF | batch_id: {local_batch_id}")
                local_batch_id += 1
                reviews_eof_sent = True

        logging.info("action: Finished sending all remaining data | result: success ✅")


    def save_current_execution(self, percent):
        with open("/data/percent.log", "w") as file:
            file.write(str(percent))

    def save_client_id_log(self, client_id):
        with open(CLIENT_ID_LOG_PATH, "w") as file:
            file.write(str(client_id))

    def run(self):
        try: 
            percent_of_file_for_use_by_execution = os.getenv("PERCENT_OF_FILE_FOR_USE_BY_EXECUTION", 1)
            self.percentages = [float(p.strip()) for p in percent_of_file_for_use_by_execution.split(',')]
            logging.info(f"Starting executions of Client")
            for i, percent in enumerate(self.percentages, 1):
                self.save_current_execution(percent)
                logging.info(f"Saving current execution with {percent*100}% of file")
                logging.info(f"Starting execution {i} of {len(self.percentages)} with {percent*100}% of file")
                self.execute(percent)
                logging.info(f"Finished execution {i} with {percent*100}%")
            logging.info("All executions completed")
        except Exception as e:
            logging.info(f"action: Error Catcheado: in Run: {e}  | result: success ✅")
            self.stop()
    
    def auth(self, client_id):
        logging.info(f"action: auth | estoy enviando el client_id: {client_id}")
        self.protocol.send_auth(client_id)
        logging.info(f"action: Se envio el auth")
        client_id_response, batch_id = self.protocol.recv_auth_result()
        logging.info(f"action: auth | result: {client_id_response, batch_id} ✅")
        if client_id_response == None or (client_id != INVALID_CLIENT_ID and (client_id_response != client_id)) or batch_id == None:
            logging.error("action: auth | result: failed ❌")
            raise Exception("Auth failed")
        
        self.config_params["id"] = client_id_response
        self.batch_id = batch_id

        self.save_client_id_log(client_id_response)

    def execute(self, percent):
        self.init_readers_and_responses(percent)
        self.connect_to_server()
        if (self.config_params["id"] is None):
            logging.info("action: Sending auth without client id")
            self.auth(INVALID_CLIENT_ID)  
        else:
            logging.info(f"action: Sending auth with client id {self.config_params['id']}")
            self.auth(self.config_params["id"])

        self.threads.append(threading.Thread(target =self.send_data))
        self.threads.append(threading.Thread(target =self.get_result_from_queries))
        for thread in self.threads:
            thread.start()
        for thread in self.threads:
            thread.join()
        self.stop()

    def get_result_from_queries(self):
        try:
            logging.info("action: Waiting for the results 📊 | result: pending ⌚")
            while not self.there_a_signal:
                resultQuerys = self.protocol.recv_result()
                if resultQuerys == None:
                    break
                logging.info(f"action: result_received 📊 | result: success ✅")
                self.actual_responses = resultQuerys.append_data(self.actual_responses)
            logging.info("action: All the results 📊 were received! ✅")
            if os.path.exists(CLIENT_ID_LOG_PATH):
                os.remove(CLIENT_ID_LOG_PATH)
                logging.info(f"action: client id log file deleted | client_id: {self.config_params['id']}")
            diff = self.expected_responses.diff(self.actual_responses)
            for query in diff:
                logging.info(f"action: diff | query: {query} | diff: {diff[query]}")
        except Exception as e:
            logging.info(f"action: Error Catch from thread Receiver: {e} | result: success ✅")

    def stop_by_signal(self):
        self.there_a_signal = True
        self.socket.close()
        self.game_reader.close()
        self.review_reader.close()

    def stop(self):
        self.socket.close()
        self.game_reader.close()
        self.review_reader.close()
        for thread in self.threads:
            thread.join()
        self.threads = []
        logging.info("action: Client stop! 🏪 | result: success ✅")