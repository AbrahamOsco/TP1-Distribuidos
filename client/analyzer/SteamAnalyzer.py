import logging
import time
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
        self.percent = 1
        self.there_a_signal = False
        self.should_send_reviews = int(os.getenv("SEND_REVIEWS", 1)) == 1
        self.max_retries = int(os.getenv("MAX_RETRIES", 10))
        self.retry_delay = int(os.getenv("RETRY_DELAY", 5)) 
        self.reconnect_lock = threading.Lock()

    def restart_readers_and_responses(self):
        self.game_reader.close()
        self.review_reader.close()
        self.init_readers_and_responses()

    def init_readers_and_responses(self):
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
        try:
            self.socket = Socket(self.config_params["hostname"], 12345)
            result, msg = self.socket.connect()
            if not result:
                logging.error(f"action: connect_to_server | result: failed ❌ | msg: {msg}")
                return False
            logging.info(f"action: connect_to_server | result: success ✅ | msg: {msg}")
            self.protocol = ClientProtocol(socket=self.socket)
            return True
        except Exception as e:
            logging.error(f"action: connect_to_server | result: failed ❌ | error: {e}")
            return False

    def reconnect(self):
        with self.reconnect_lock:
            if self.socket.is_active():
                return True
            self.restart_readers_and_responses()
            attempts = 0
            while attempts < self.max_retries:
                logging.info(f"action: reconnect | attempt: {attempts + 1}/{self.max_retries}")
                if self.connect_to_server():
                    try:
                        logging.info("action: reconnect | result: success ✅")
                        self.auth(self.config_params["id"])
                        logging.info("action: auth reenviado | result: success ✅")
                        return True
                    except Exception as e:
                        logging.error(f"action: reconnect | error: {e}")
                attempts += 1
                time.sleep(self.retry_delay)
            
            logging.error("action: reconnect | result: failed after all retry attempts ❌")
            self.stop_by_signal()
            return False

    def send_data(self):
        while not self.there_a_signal:
            try:
                self.find_and_send_remaining_data()
                break
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError) as e:
                logging.error(f"action: send_data | error: {e} | attempting reconnect")
                if not self.reconnect():
                    break
                logging.info("action: send_data | reenviado")
            except Exception as e:
                logging.error(f"action: send_data | unexpected error: {e}")
                self.stop()
                break

    def find_and_send_remaining_data(self):
        logging.info("action: Finding and sending remaining data | result: pending ⌚")
        local_batch_id = 1
        show_message = True
        while not self.there_a_signal:
            some_games = self.game_reader.get_next_batch()
            if some_games is None:
                logging.info("action: No more game batches left to process.")
                break

            if local_batch_id < self.batch_id:
                logging.debug(f"action: Skipping game batch | local_batch_id: {local_batch_id}")
                local_batch_id += 1
                continue

            self.protocol.send_data_raw(GamesRawDTO(games_raw=some_games, batch_id=self.batch_id))
            if show_message:
                logging.info(f"action: Start sending games from batch batch_id: {local_batch_id} ✅")
                show_message = False

            self.batch_id += 1
            local_batch_id += 1
        logging.info("action: All The game 🕹️ batches were sent! | result: success ✅")

        if not self.there_a_signal and local_batch_id == self.batch_id:
            self.protocol.send_games_eof(self.batch_id)
            logging.info(f"action: Sent games EOF | batch_id: {self.batch_id}")
            self.batch_id += 1
        local_batch_id += 1

        if self.should_send_reviews:
            logging.info("action: Sending Reviews | result: pending ⌚")
            while not self.there_a_signal:
                some_reviews = self.review_reader.get_next_batch()
                if some_reviews is None:
                    logging.info("action: No more review batches left to process.")
                    break

                if local_batch_id < self.batch_id:
                    logging.debug(f"action: Skipping review batch | local_batch_id: {local_batch_id}")
                    local_batch_id += 1
                    continue

                self.protocol.send_data_raw(ReviewsRawDTO(reviews_raw=some_reviews, batch_id=self.batch_id))
                if show_message:
                    logging.info(f"action: Start sending reviews from batch batch_id: {local_batch_id} ✅")
                    show_message = False
                self.batch_id += 1
                local_batch_id += 1
            logging.info("action: All the reviews 📰 batches were sent! | result: success ✅")
            if not self.there_a_signal and local_batch_id == self.batch_id:
                self.protocol.send_reviews_eof(self.batch_id)
                logging.info(f"action: Sent reviews EOF | batch_id: {self.batch_id}")
                self.batch_id += 1
            local_batch_id += 1

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
            inicio = time.time()
            for i, percent in enumerate(self.percentages, 1):
                self.save_current_execution(percent)
                logging.info(f"Saving current execution with {percent*100}% of file")
                logging.info(f"Starting execution {i} of {len(self.percentages)} with {percent*100}% of file")
                self.execute(percent)
                logging.info(f"Finished execution {i} with {percent*100}%")
            logging.info("All executions completed")
            fin = time.time()
            logging.info(f"Total time: {fin - inicio:.5f} segundos")
        except Exception as e:
            logging.info(f"action: Error Catcheado: in Run: {e}  | result: success ✅")
            self.stop()
    
    def auth(self, client_id):
        logging.info(f"action: auth | estoy enviando el client_id: {client_id}")
        self.protocol.send_auth(client_id)
        logging.info(f"action: Se envio el auth")
        client_id_response, batch_id = self.protocol.recv_auth_result()
        logging.info(f"action: auth | result: {client_id_response, batch_id+1} ✅")
        if client_id_response == None or (client_id != INVALID_CLIENT_ID and (client_id_response != client_id)) or batch_id == None:
            logging.error("action: auth | result: failed ❌")
            raise Exception("Auth failed")
        
        self.config_params["id"] = client_id_response
        self.batch_id = batch_id+1

        self.save_client_id_log(client_id_response)

    def execute(self, percent):
        self.percent = percent
        self.config_params["id"] = self.get_client_id()
        self.init_readers_and_responses()
        if not self.connect_to_server():
            logging.error("action: execute | result: failed to establish initial connection")
            self.reconnect()

        if self.config_params["id"] is None:
            logging.info("action: Sending auth without client id")
            self.auth(INVALID_CLIENT_ID)
        else:
            logging.info(f"action: Sending auth with client id {self.config_params['id']}")
            self.auth(self.config_params["id"])

        self.threads.append(threading.Thread(target=self.send_data))
        self.threads.append(threading.Thread(target=self.get_result_from_queries))
        for thread in self.threads:
            thread.start()
        for thread in self.threads:
            thread.join()
        self.stop()

    def get_result_from_queries(self):
        while not self.there_a_signal:
            try:
                logging.info("action: Waiting for the results 📊 | result: pending ⌚")
                while not self.there_a_signal:
                    resultQuerys = self.protocol.recv_result()
                    if resultQuerys is None:
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
                break
            except Exception as e:
                logging.info(f"action: Error Catch from thread Receiver: {e} | result: success ✅")
                if not self.reconnect():
                    break

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