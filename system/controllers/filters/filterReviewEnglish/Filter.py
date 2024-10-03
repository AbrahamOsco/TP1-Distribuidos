import logging
from system.commonsSystem.node.node import Node
import langid

class Filter(Node):
    def __init__(self):
        super().__init__()

    def is_in_english(self, text):
        lang, _ = langid.classify(text)
        return lang == 'en'
    
    def trim_data(self, data):
        return data.retain(["client", "id"])

    def send_review(self, data):
        self.broker.public_message(exchange_name=self.sink, message=self.trim_data(data).to_string())

    def process_data(self, data):
        if self.is_in_english(data["review_text"]):
            self.send_review(data)