import logging
import os
import multiprocessing
from broker.Broker import Broker

class Node:
    def __init__(self):
        self.initialize_config()
        self.running = True
        self.processes = []
        self.node_name = os.getenv("NODE_NAME")
        self.node_id = os.getenv("NODE_ID")
        manager = multiprocessing.Manager()
        self.processing_lock = manager.Lock()
        self.clients_lock = manager.Lock()
        self.shared_data = manager.list()
        if self.amount_of_nodes is None:
            self.amount_of_nodes = 1
        if self.amount_of_nodes > 1:
            self.processes.append(multiprocessing.Process(target=self.inform_eof_to_nodes))

    def initialize_queues(self):
        self.broker = Broker()
        ## Source and destination for all workers
        self.broker.create_queue(queue_name=self.source_queue)
        self.broker.create_queue(queue_name=self.sink_queue)
        self.broker.create_exchange(exchange_type="direct", exchange_name=self.sink_queue)
        self.broker.bind_queue(queue_name=self.sink_queue, exchange_name=self.sink_queue, routing_key=self.sink_queue)
        if self.amount_of_nodes < 2:
            return
        ## Confirmation queue shared amongs workers
        self.broker.create_queue(queue_name=self.node_name + "_confirmation")
        self.broker.create_exchange(exchange_type="direct", exchange_name=self.node_name + "_confirmation")
        self.broker.bind_queue(queue_name=self.node_name + "_confirmation", exchange_name=self.node_name + "_confirmation", routing_key='')
        ## Fanout for EOFs
        self.broker.create_queue(queue_name=self.node_name + self.node_id + "_eofs")
        self.broker.create_exchange(exchange_type="fanout", exchange_name=self.node_name + "_eofs")
        self.broker.bind_queue(queue_name=self.node_name + self.node_id + "_eofs", exchange_name=self.node_name + "_eofs", routing_key='')

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

    def receive_data(self):
        data = []
        return data
    
    def is_eof(self, data):
        return data == "EOF"
    
    def send_result(self):
        pass

    def send_eof(self, client):
        ## SEND EOF TO NEXT NODE
        pass

    def send_eof_confirmation(self, client):
        ## SEND EOF CONFIRMATION TO ORIGINAL NODE
        pass

    def wait_for_confirmation(self, client):
        ## READ FROM CONFIRMATION QUEUE
        while self.running:
            ## IF ALL CONFIRMATIONS RECEIVED
            break
        with self.clients_lock:
            self.shared_data.remove(client)
        self.send_eof(client)

    def inform_eof_to_nodes(self, client):
        if self.amount_of_nodes < 2:
            self.send_eof(client)
            return
        with self.clients_lock:
            self.shared_data.append(client)
        self.processes.append(multiprocessing.Process(target=self.wait_for_confirmation))
        #SEND EOF TO FANOUT

    def receive_nodes_eofs(self):
        client = None ## READ FROM FANOUT
        return client
    
    def process_node_eof(self, client):
        self.send_eof_confirmation(client)
        with self.clients_lock:
            self.shared_data.remove(client)

    def read_nodes_eofs(self):
        while self.running:
            try:
                client = self.receive_nodes_eofs()
                with self.processing_lock:
                    self.process_node_eof(client)
            except Exception as e:
                logging.error(f"action: error | result: {e}")

    def process_data(self, data):
        if self.is_eof(data):
            return
        
    def run(self):
        while self.running:
            try:
                data = self.receive_data()
                with self.processing_lock:
                    self.process_data(data)
            except Exception as e:
                logging.error(f"action: error | result: {e}")
    
    def stop(self):
        self.running = False
        self.broker.close()
        for process in self.processes:
            process.join()