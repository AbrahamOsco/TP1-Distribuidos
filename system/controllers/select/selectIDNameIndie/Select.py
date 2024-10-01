from system.commonsSystem.node.node import Node

class Select(Node):
    def __init__(self):
        super().__init__()
    
    def trim_data(self, data):
        return data.retain(["client", "id", "name"])

    def send_game(self, data):
        self.broker.public_message(exchange_name=self.sink, message=self.trim_data(data).to_string())

    def process_data(self, data):
        self.send_game(data)