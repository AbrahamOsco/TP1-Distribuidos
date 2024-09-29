import logging
import os
from broker.Broker import Broker

class Node:
    def __init__(self):
        self.initialize_config()
        self.running = True
        self.processes = []
        self.node_name = os.getenv("NODE_NAME")
        self.node_id = os.getenv("NODE_ID")
        self.clients = []
        self.confirmations = 0
        if self.amount_of_nodes is None:
            self.amount_of_nodes = 1

    def initialize_queues(self):
        self.broker = Broker()
        ## Source and destination for all workers
        self.broker.create_queue(queue_name=self.source_queue, callback=self.process_queue_message)
        self.broker.create_queue(queue_name=self.sink_queue)
        self.broker.create_exchange(exchange_type="direct", exchange_name=self.sink_queue)
        self.broker.bind_queue(queue_name=self.sink_queue, exchange_name=self.sink_queue, routing_key=self.sink_queue)
        if self.amount_of_nodes < 2:
            return
        ## Confirmation queue shared amongs workers
        self.broker.create_queue(queue_name=self.node_name + self.node_id + "_confirmation")
        self.broker.create_exchange(exchange_type="direct", exchange_name=self.node_name + "_confirmation")
        self.broker.bind_queue(queue_name=self.node_name + "_confirmation", exchange_name=self.node_name + "_confirmation")
        ## Fanout for EOFs
        self.broker.create_queue(queue_name=self.node_name + self.node_id + "_eofs", callback=self.read_nodes_eofs)
        self.broker.create_exchange(exchange_type="fanout", exchange_name=self.node_name + "_eofs")
        self.broker.bind_queue(queue_name=self.node_name + self.node_id + "_eofs", exchange_name=self.node_name + "_eofs")

    def initialize_config(self):
        self.config_params = {}
        self.config_params["id"] = int(os.getenv("CLI_ID"))
        self.config_params["log_level"] = os.getenv("CLI_LOG_LEVEL")
        self.initialize_log()

    def initialize_log(self):
        logging.basicConfig(
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=self.config_params["log_level"],
            datefmt='%Y-%m-%d %H:%M:%S',
        )
    
    def is_eof(self, data):
        return data == "EOF"
    
    def send_result(self):
        pass

    def send_eof(self, client):
        self.broker.public_message(exchange_name=self.sink_queue, message=client) ## CHANGE FOR EOF WITH CLIENT

    def send_eof_confirmation(self, client):
        self.broker.public_message(exchange_name=self.node_name + "_confirmation", message=client) ## CHANGE FOR EOF WITH CLIENT

    def check_confirmations(self, client):
        self.confirmations += 1
        if self.confirmations == self.amount_of_nodes:
            self.clients.remove(client)
            self.send_eof(client)
            self.confirmations = 0
            self.broker.stop_listening_queue(name=self.node_name + "_confirmation")

    def read_eofs_confirmations(self, ch, method, properties, body):
        try:
            data = body.decode()
            self.check_confirmations(data)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logging.error(f"action: error | result: {e}")

    def inform_eof_to_nodes(self, client):
        if self.amount_of_nodes < 2:
            self.send_eof(client)
            return
        self.confirmations = 1
        self.broker.start_listening_queue(name=self.node_name + "_confirmation", callback=self.read_eofs_confirmations)
        self.broker.public_message(exchange_name=self.node_name + "_eofs", message=client) ##Change for eofs
    
    def process_node_eof(self, client):
        self.send_eof_confirmation(client)
        self.clients.remove(client)

    def read_nodes_eofs(self, ch, method, properties, body):
        try:
            if self.confirmations == 0:
                data = body.decode()
                self.process_node_eof(data)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logging.error(f"action: error | result: {e}")

    def process_data(self, data):
        if self.is_eof(data):
            return
        
    def process_queue_message(self, ch, method, properties, body):
        try:
            data = body.decode()
            self.process_data(data)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logging.error(f"action: error | result: {e}")

    def run(self):
        self.broker.start_consuming()
    
    def stop(self):
        self.broker.close()