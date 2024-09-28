import logging
from common.node.node import Node
import langid

class Filter(Node):
    def __init__(self):
        super()

    def receive_data(self):
        data = []
        return data
    
    def send_eof(self):
        logging.info("action: eof")

    def is_in_english(self, text):
        lang, _ = langid.classify(text)
        return lang == 'en'
    
    def send_review(self, data):
        logging.info(f"action: result | id: {data['id']}")

    def process_data(self, data):
        if self.is_eof(data):
            self.send_eof()
            return
        if self.is_in_english(data["review_text"]):
            self.send_review(data)