"""import os
from system.commonsSystem.node.node import Node, UnfinishedBusinessException
from system.commonsSystem.DTO.ReviewedGameDTO import ReviewedGameDTO

STATUS_STARTED = 0
STATUS_REVIEWING = 1

class Storage(Node):
    def __init__(self):
        super().__init__()
        self.reset_list()
        self.amount_needed = os.getenv("AMOUNT_NEEDED")

    def reset_list(self):
        self.list = {}
        self.top_5_heap = []
        self.status = STATUS_STARTED

    def inform_eof_to_nodes(self, client):
        if self.status == STATUS_REVIEWING:
            self.send_result()
            self.send_eof(client)
            self.reset_list()
            self.status = STATUS_STARTED
        else:
            self.status = STATUS_REVIEWING

    def send_result(self):
        for app_id in self.list:
            data = ReviewedGameDTO(app_id, self.list[app_id])
            self.broker.public_message(exchange_name=self.sink, message=data, routing_key="default")

    def process_data(self, data):
        if data.is_review():
            if self.status == STATUS_STARTED:
                raise UnfinishedBusinessException()
            if data.app_id in self.list:
                self.list[data.app_id] += 1
        if data.is_game():
            if self.status == STATUS_REVIEWING:
                raise UnfinishedBusinessException()
            self.list.add(data.name)"""