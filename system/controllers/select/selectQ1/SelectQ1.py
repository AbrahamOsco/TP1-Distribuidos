from common.utils.utils import initialize_log 
from system.commonsSystem.broker.Broker import Broker
import logging
import time as t
import os
from system.commonsSystem.protocol.ServerProtocol import ServerProtocol

def callback_generica(ch, method, properties, body):
    logging.info(f"Se Recibe : 👉 Decode:{body.decode()} with routing key: {method.routing_key}")
    t.sleep(2)
    logging.info(f" Message ready! 🔨 🛠️ 🇱")
    ch.basic_ack(delivery_tag=method.delivery_tag)

class SelectQ1:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.broker = Broker()
        self.broker.create_exchange(name='games_reviews_input', exchange_type='topic')
        pass
    
    def filter_fields_game(self):
        pass

    def run(self):
        logging.info("action: Start listening from queue: games_q1 | result: pending ⌚")
        games_q1 = self.broker.create_queue(durable =True, callback =callback_generica)
        # con * se remplaza exactmaente una word ej : games.q1.* => games.q1.helloWorld
        # con # se remplaza zero o mas words ej: games.q1.# => games.q1 
        self.broker.bind_queue(exchange_name='games_reviews_input', queue_name =games_q1, binding_key='games.q1.hello')
        logging.info("action: Start listening from queue: games_q1 | result: sucess ✅")
        self.broker.start_consuming()
        logging.info("action: Start consuming from queue: games_q1 | result: sucess ✅ 🤯")
        # si llega el EOF: 
        # Solo hacer el close cuando recibamos la signal y acabe todo ordenado!!. 
        # self.broker.close()