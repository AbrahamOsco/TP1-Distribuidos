from system.commonsSystem.node.node import Node

class FilterNode(Node):
    def __init__(self, state):
        super().__init__()
        self.state = state

    def fulfills_criteria(self, element):
        return False

    def send_data(self, data):
        data.set_state(self.state)
        self.broker.public_message(sink=self.sink, message=data.serialize(), routing_key="default")

    def process_data(self, data):
        data.filter_data(lambda x: self.fulfills_criteria(x))
        if data.get_amount() > 0:
            self.send_data(data)