import logging
from system.commonsSystem.DTO.PlatformDTO import PlatformDTO
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.GameDTO import GameDTO

COUNT_BY_PLATFORM = "CountByPlatform"
RK_COUNT_BY_PLATFORM= "count_by_platform"

class Counter:
    def __init__(self):
        #super().__init__()
        #self.reset_counter()
        self.broker = Broker()
        self.broker.create_exchange(name='selectq1_to_platform_counter', exchange_type='direct')
        self.broker.create_exchange(name=COUNT_BY_PLATFORM, exchange_type='direct')
        games_platform_queue_name = self.broker.create_queue(durable=True, callback=self.handler_callback_games_platform())
        self.broker.bind_queue(exchange_name='selectq1_to_platform_counter', queue_name=games_platform_queue_name, binding_key='sq1.pc')

        count_by_platform_queue_name = self.broker.create_queue(durable=True, callback=self.handler_callback_count_by_platform())
        self.broker.bind_queue(exchange_name=COUNT_BY_PLATFORM, queue_name=count_by_platform_queue_name, binding_key=RK_COUNT_BY_PLATFORM)
        self.platform = PlatformDTO(client_id=0, windows=0, mac=0, linux=0)
        self.reducer = PlatformDTO(client_id=0, windows=0, mac=0, linux=0)
    def run(self):
        logging.info("action: Counter started| result: sucess ✅ 🔥")
        self.broker.start_consuming()

    def handler_callback_games_platform(self):
        def handler_message(ch, method, properties, body):
            result = self.broker.get_message(body)
            for game in result.games_dto:
                logging.info(f"Win: {game.windows} Linux: {game.linux}, Mac: {game.mac} ⏰ 🧮 🚡 ")
                self.process_data(game)
            
            #self.pre_eof_actions()
            ch.basic_ack(delivery_tag=method.delivery_tag)
            #TODO: Agregar logica para enviar el mensaje al reducer cuando llega el EOF       
            self.broker.public_message(exchange_name=COUNT_BY_PLATFORM ,
                                        routing_key=RK_COUNT_BY_PLATFORM, message =self.platform)
            
        return handler_message


    def handler_callback_count_by_platform(self):
        def handler_message(ch, method, properties, body):
            result = self.broker.get_message(body)
            logging.info(f"Win: {result.windows} Linux: {result.linux}, Mac: {result.mac} ⏰ 🧮 🚡 ")
            self.reduce_data(result)
            
            #self.pre_eof_actions()
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        return handler_message

    def process_data(self, game):
        # self.platform.client_id = game.client_id
        self.platform.windows += game.windows
        self.platform.mac += game.mac
        self.platform.linux += game.linux
        logging.info(f"Informacion procesada que se enviara al reducer")
        logging.info(f"Win: {self.platform.windows} Linux: {self.platform.linux}, Mac: {self.platform.mac} ⏰ 🧮 🚡 ")

    def reduce_data(self, platform):
        # self.reducer.client_id = platform.client_id
        self.reducer.windows += platform.windows
        self.reducer.mac += platform.mac
        self.reducer.linux += platform.linux

#    def reset_counter(self):
#        self.result = {
#            "client_id": "",
#            "windows": 0,
#            "linux": 0,
#            "mac": 0,
#        }
#
#    def pre_eof_actions(self):
#        self.send_result(self.result)
#        self.reset_counter()
#
#    def trim_data(self, data):
#        return GameDTO(windows=data["windows"], linux=data["linux"], mac=data["mac"])
#
#    def send_result(self, data):
#        logging.info(f"action: send_result | data: {data}")
#        self.broker.public_message(exchange_name=self.sink, message=self.trim_data(data).to_string(), routing_key="default")
#

