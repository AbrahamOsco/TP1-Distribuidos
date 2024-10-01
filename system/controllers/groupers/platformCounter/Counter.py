import logging
from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.GameDTO import GameDTO

class Counter(Node):
    def __init__(self):
        super().__init__()
        self.reset_counter()
        self.broker.create_exchange(name='selectq1_to_platform_counter', exchange_type='direct')
        queue_name = self.broker.create_queue(durable =True, callback = self.handler_callback())
        self.broker.bind_queue(exchange_name='selectq1_to_platform_counter', queue_name =queue_name, binding_key='sq1.pc')

    def handler_callback(self):
        def handler_message(ch, method, properties, body):
            result = self.broker.get_message(body)
            for game in result.games_dto:
                logging.info(f"Win: {game.windows} Linux: {game.linux}, Mac: {game.mac} ⏰ 🧮 🚡 ")
            self.process_data(result)
            self.pre_eof_actions()
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_message

    def reset_counter(self):
        self.result = {
            "client_id": "",
            "windows": 0,
            "linux": 0,
            "mac": 0,
        }

    def pre_eof_actions(self):
        self.send_result(self.result)
        self.reset_counter()

    def trim_data(self, data):
        return GameDTO(windows=data["windows"], linux=data["linux"], mac=data["mac"])

    def send_result(self, data):
        logging.info(f"action: send_result | data: {data}")
        self.broker.public_message(exchange_name=self.sink, message=self.trim_data(data).to_string(), routing_key="default")

    def process_data(self, data):
        #self.result["client_id"] = data.client_id HERE need a fix @FRANCO you should use now the new dto that will be created soon! 
        self.result["windows"] += data.windows
        self.result["linux"] += data.linux
        self.result["mac"] += data.mac