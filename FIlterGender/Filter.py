import logging
from common.node.node import Node

class Filter(Node):
    def __init__(self):
        super()

    def receive_data(self):
        data = []
        return data
    
    def process_data(self, data):
        if self.is_eof(data):
            return