from common.utils.utils import initialize_log
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.broker.Broker import Broker
import logging
import time as t
import os
from system.commonsSystem.protocol.ServerProtocol import ServerProtocol

class SelectQ1:
    
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.broker = Broker()
        self.broker.create_exchange(name='games_reviews_input', exchange_type='direct')
        queue_name = self.broker.create_queue(durable =True, callback = self.handler_callback())
        self.broker.bind_queue(exchange_name='games_reviews_input', queue_name =queue_name, binding_key='games.q1')
        logging.info("action: Start listening from queue: games_q1 | result: sucess ✅")
    
    def handler_callback(self):
        def handler_message(ch, method, properties, body):
            result = self.broker.get_message(body)
            for game in result.games_dto:
                logging.info(f"🔥Se Recibe : 👉🤯{game.app_id}| {game.name}| {game.genres} with routing key: {method.routing_key}")
            t.sleep(2)
            logging.info(f" Message ready! 🔨 🛠️ 🇱")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_message
    
    def filter_platform(self, batch_game: GamesDTO):
        pass


    def run(self):
        logging.info("action: Start consuming from queue: games_q1 | result: sucess ✅ 🤯")
        self.broker.start_consuming()
        # Solo hacer el close cuando recibamos la signal y acabe todo ordenado!!. 
        # self.broker.close()

