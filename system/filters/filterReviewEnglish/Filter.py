import logging
from commonsSystem.node.node import Node
import langid

class Filter(Node):
    def __init__(self):
        super()

    def receive_data(self):
        data = []
        return data

    def is_in_english(self, text):
        lang, _ = langid.classify(text)
        return lang == 'en'
    
    def trim_data(self, data):
        return data['id']

    def send_review(self, data):
        logging.info(f"action: result | {self.trim_data(data)}")

    def process_data(self, data):
        if self.is_eof(data):
            self.send_eof()
            return
        if self.is_in_english(data["review_text"]):
            self.send_review(data)