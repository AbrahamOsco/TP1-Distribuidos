from common.utils.utils import initialize_log
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_PLATFORM
from system.commonsSystem.DTO.GameDTO import GameDTO
from system.commonsSystem.broker.Broker import Broker
import logging
import time as t
import os
from system.commonsSystem.protocol.ServerProtocol import ServerProtocol

FILTERBASIC_INPUT = "filterbasic.input"
RK_GATEWAY_SELECTQ1= "games.q1"
EXCHANGE_SELECTQ1_COUNTER = "selectq1_to_platform_counter"

class SelectQ1:
    
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.broker = Broker()
        self.broker.create_exchange(name =FILTERBASIC_INPUT, exchange_type ='direct')
        self.broker.create_exchange(name =EXCHANGE_SELECTQ1_COUNTER, exchange_type ='direct')
        queue_name = self.broker.create_queue(durable =True, callback = self.handler_callback())
        self.broker.bind_queue(exchange_name =FILTERBASIC_INPUT, queue_name =queue_name, binding_key =RK_GATEWAY_SELECTQ1)
        logging.info(f"action: SelectQ1 is bound to the exchange {FILTERBASIC_INPUT} 🗡️ | result: sucess ✅")
    
    def handler_callback(self):
        def handler_message(ch, method, properties, body):
            result = self.broker.get_message(body)
            self.filter_platform(result)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_message
    
    def filter_platform(self, batch_game: GamesDTO):
        games_dto = []
        for game in batch_game.games_dto:
            games_dto.append(GameDTO(windows=game.windows, mac=game.mac, linux=game.linux))
        new_gamesDTO = GamesDTO(client_id =batch_game.client_id, state_games = STATE_PLATFORM, games_dto = games_dto)
        self.broker.public_message(exchange_name='selectq1_to_platform_counter', routing_key='sq1.pc', message = new_gamesDTO)
        logging.info(f"action: Send GamesDTO 🏑 to platform_counter | count: {len(new_gamesDTO.games_dto)} | result: success ✅")

    def run(self):
        self.broker.start_consuming()
        # self.broker.close() # Solo hacer el close cuando recibamos la signal y acabe todo ordenado!!. 

