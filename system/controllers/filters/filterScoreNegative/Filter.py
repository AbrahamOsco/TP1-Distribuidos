from system.commonsSystem.node.node import Node

class Filter(Node):
    def __init__(self):
        super().__init__()
    
    def trim_data(self, data):
        return data.retain(["client", "id", "review_text"])

    def send_review(self, data):
        self.broker.public_message(exchange_name=self.sink, message=self.trim_data(data).to_string())

    def process_data(self, data):
        if data["review_score"] == 0:
            self.send_review(data)