import logging
import os
from broker.Broker import Broker
from DTO.EOFDTO import EOFDTO
from DTO.DTO import getDTO

class Node:
    def __init__(self):
        self.initialize_config()
        self.running = True
        self.processes = []
        self.node_name = os.getenv("NODE_NAME")
        self.node_id = os.getenv("NODE_ID")
        self.clients = []
        self.clients_pending_confirmations = []
        self.confirmations = 0
        if self.amount_of_nodes is None:
            self.amount_of_nodes = 1

    def initialize_queues(self):
        self.broker = Broker()
        ## Source and destination for all workers
        self.broker.create_queue(queue_name=self.source, callback=self.process_queue_message)
        self.broker.create_exchange(exchange_type="direct", exchange_name=self.source)
        self.broker.bind_queue(queue_name=self.source, exchange_name=self.source)
        self.broker.create_exchange(exchange_type="direct", exchange_name=self.sink)
        if self.amount_of_nodes < 2:
            return
        ## Fanout for EOFs
        eof_queue = self.broker.create_queue(callback=self.read_nodes_eofs)
        self.broker.create_exchange(exchange_type="fanout", exchange_name=self.node_name + "_eofs")
        self.broker.bind_queue(queue_name=eof_queue, exchange_name=self.node_name + "_eofs")

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
        self.broker.public_message(exchange_name=self.sink, message=EOFDTO(client, False).to_string())

    def send_eof_confirmation(self, client):
        self.broker.public_message(exchange_name=self.node_name + "_eofs", message=EOFDTO(client,True).to_string())

    def check_confirmations(self, client):
        self.confirmations += 1
        if self.confirmations == self.amount_of_nodes:
            self.clients.remove(client)
            self.clients_pending_confirmations.remove(client)
            self.send_eof(client)
            self.confirmations = 0

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
        self.clients_pending_confirmations.append(client)
        self.broker.public_message(exchange_name=self.node_name + "_eofs", message=EOFDTO(client, False).to_string())
    
    def process_node_eof(self, data):
        if data.client in self.clients_pending_confirmations:
            if data.is_confirmation():
                self.check_confirmations(data.client)
            return
        self.send_eof_confirmation(data.client)
        self.clients.remove(data.client)

    def read_nodes_eofs(self, ch, method, properties, body):
        try:
            data = body.decode()
            self.process_node_eof(EOFDTO.from_string(data))
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logging.error(f"action: error | result: {e}")

    def process_data(self, data):
        pass
        
    def check_new_client(self, data):
        if data.get_client() not in self.clients:
            self.clients.append(data.get_client())

    def process_queue_message(self, ch, method, properties, body):
        try:
            data = getDTO(body.decode())
            if data.is_EOF():
                self.inform_eof_to_nodes(data.get_client())
            else:
                self.check_new_client(data)
                self.process_data(data)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logging.error(f"action: error | result: {e}")

    def run(self):
        self.broker.start_consuming()
    
    def stop(self):
        self.broker.close()