import logging
import os
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.EOFDTO import EOFDTO
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.DTO.enums.OperationType import OperationType

class UnfinishedGamesException(Exception):
    pass

class UnfinishedReviewsException(Exception):
    pass

class Node:
    def __init__(self):
        self.initialize_config()
        self.running = True
        self.processes = []
        self.node_name = os.getenv("NODE_NAME")
        self.node_id = os.getenv("NODE_ID")
        self.source = os.getenv("SOURCE").split(',')
        self.source_key = os.getenv("SOURCE_KEY", "default").split(',')
        self.source_type = os.getenv("SOURCE_TYPE", "direct").split(',')
        self.sink = os.getenv("SINK")
        self.sink_type = os.getenv("SINK_TYPE", "direct")
        self.amount_of_nodes = int(os.getenv("AMOUNT_OF_NODES", 1))
        self.clients = []
        self.clients_pending_confirmations = []
        self.confirmations = 0
        self.node_stats = {}
        self.broker = Broker()
        self.initialize_queues()


    def initialize_queues(self):
        ## Source and destination for all workers
        for i, source in enumerate(self.source):
            self.broker.create_source(name=self.node_name, callback=self.process_queue_message)
            self.broker.create_sink(type=self.source_type[i], name=source)
            self.broker.bind_queue(queue_name=self.node_name, sink=source, routing_key=self.source_key[i])
        self.broker.create_sink(type=self.sink_type, name=self.sink)
        if self.amount_of_nodes < 2:
            return
        ## Fanout for EOFs
        eof_queue = self.broker.create_source(callback=self.read_nodes_eofs)
        self.broker.create_sink(type="fanout", name=self.node_name + "_eofs")
        self.broker.bind_queue(queue_name=eof_queue, sink=self.node_name + "_eofs")

    def initialize_config(self):
        self.config_params = {}
        self.config_params["log_level"] = os.getenv("LOGGING_LEVEL", "INFO")
        self.initialize_log()

    def initialize_log(self):
        logging.basicConfig(
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=self.config_params["log_level"],
            datefmt='%Y-%m-%d %H:%M:%S',
        )

    def update_node_stats(self, client_id, games=0, reviews=0):
        if client_id not in self.node_stats:
            self.node_stats[client_id] = {'games': 0, 'reviews': 0}
        
        self.node_stats[client_id]['games'] += games
        self.node_stats[client_id]['reviews'] += reviews

    def send_eof(self, client):
        self.broker.public_message(sink=self.sink, message=EOFDTO(OperationType.OPERATION_TYPE_GAMES_EOF_DTO, client, False, self.node_stats[client]['games'] ).serialize(), routing_key='default')

    def send_eof_confirmation(self, client):
        self.broker.public_message(sink=self.node_name + "_eofs", message=EOFDTO(OperationType.OPERATION_TYPE_GAMES_EOF_DTO, client,True, self.node_stats[client]['games']).serialize())

    def check_confirmations(self, client):
        self.confirmations += 1
        logging.info(f"action: check_confirmations | client: {client} | confirmations: {self.confirmations}")
        if self.confirmations == self.amount_of_nodes:
            self.clients.remove(client)
            self.clients_pending_confirmations.remove(client)
            self.send_eof(client)
            self.confirmations = 0

    def process_node_eof(self, data):
        if data.client in self.clients_pending_confirmations:
            if data.is_confirmation():
                self.check_confirmations(data.client)
            return
        if data.is_confirmation():
            return
        if data.client not in self.clients:
            return
        self.pre_eof_actions()
        self.send_eof_confirmation(data.client)
        self.clients.remove(data.client)

    def inform_eof_to_nodes(self, client):
        logging.info(f"action: inform_eof_to_nodes | client: {client}")
        self.pre_eof_actions()
        if self.amount_of_nodes < 2:
            self.send_eof(client)
            return
        self.confirmations = 1
        self.clients_pending_confirmations.append(client)
        logging.info(f"action: inform_eof_to_nodes | client: {client} | pending_confirmations: {self.clients_pending_confirmations}")
        self.broker.public_message(sink=self.node_name + "_eofs", message=EOFDTO(client, False).serialize())

    def read_nodes_eofs(self, ch, method, properties, body):
        try:
            data = self.broker.get_message(body)
            self.process_node_eof(data)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logging.error(f"action: error | result: {e}")
        
    def check_new_client(self, data):
        if data.get_client() not in self.clients:
            self.clients.append(data.get_client())

    def process_queue_message(self, ch, method, properties, body):
        try:
            data = DetectDTO(body).get_dto()
            if data.is_EOF():
                self.inform_eof_to_nodes(data.get_client())
            else:
                self.check_new_client(data)
                self.process_data(data)
                if data.games_dto:
                    self.update_node_stats(client_id=data.get_client(), games=data.get_amount_of_games(), reviews=0)
                elif data.reviews_dto:
                    self.update_node_stats(client_id=data.get_client(), games=0, reviews=data.get_amount_of_reviews())
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except UnfinishedGamesException as e:
            logging.info(f"action: error | Unfinished Games Exception")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        except UnfinishedReviewsException as e:
            logging.info(f"action: error | Unfinished Reviews Exception")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        except Exception as e:
            logging.error(f"action: error | result: {e}")

    def run(self):
        self.broker.start_consuming()
    
    def stop(self):
        self.broker.close()
    
    def pre_eof_actions(self):
        """ This method can be implemented by the child class 
         Send the result of the processing to the next node 
         Will be executed when receiving an EOF """
        self.send_result()

    def send_result(self):
        """This method should be implemented by the child class 
        Send the result of the processing to the next node 
        Called by pre_eof_actions"""
        pass

    
    def process_data(self, data):
        pass
        self.broker.close()
