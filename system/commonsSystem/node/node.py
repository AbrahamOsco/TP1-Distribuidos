import logging
import os
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.EOFDTO import EOFDTO, STATE_OK, STATE_COMMIT, STATE_FINISH, STATE_DEFAULT
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.DTO.enums.OperationType import OperationType

class UnfinishedGamesException(Exception):
    pass

class UnfinishedReviewsException(Exception):
    pass

class PrematureEOFException(Exception):
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
        self.amount_received_by_node = {}
        self.amount_sent_by_node = {}
        self.total_amount_received = {}
        self.total_amount_sent = {}
        self.expected_total_amount_received = {}
        self.broker = Broker()
        self.initialize_queues()

    def initialize_queues(self):
        ## Source and destination for all workers
        for i, source in enumerate(self.source):
            if i >= len(self.source_key) or i >= len(self.source_type):
                raise ValueError("Mismatched list sizes: source, source_key, and source_type must have the same length")
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

    def update_amount_received_by_node(self,client_id, amount=0):
        if client_id not in self.amount_received_by_node:
            self.amount_received_by_node[client_id] = 0
        
        self.amount_received_by_node[client_id] += amount
       
    def update_amount_sent_by_node(self,client_id, amount=0):
        if client_id not in self.amount_sent_by_node:
            self.amount_sent_by_node[client_id] = 0
        
        self.amount_sent_by_node[client_id] += amount
   
    def update_total_amount_received(self,client, amount=0):
        if client not in self.total_amount_received:
            self.total_amount_received[client] = 0
        
        self.total_amount_received[client] += amount
 
    def update_total_amount_sent(self,client, amount=0):
        if client not in self.total_amount_sent:
            self.total_amount_sent[client] = 0
        
        self.total_amount_sent[client] += amount

    
    def send_eof(self, data):
        logging.info(f"action: send_eof | client: {data.get_client()} | total_amount_sent: {self.total_amount_sent[data.get_client()]}")
        self.broker.public_message(sink=self.sink, message=EOFDTO(data.operation_type, data.get_client(),STATE_DEFAULT,"",0,self.total_amount_sent[data.get_client()]).serialize(), routing_key='default')

    def send_eof_confirmation(self, data: EOFDTO):
        client = data.get_client()
        amount_received_by_node = self.amount_received_by_node[client]
        amount_sent_by_node = self.amount_sent_by_node[client]
        logging.debug(f"action: send_eof_confirmation | client: {client} | amount_received_by_node: {amount_received_by_node} | amount_sent_by_node: {amount_sent_by_node}")
        self.broker.public_message(sink=self.node_name + "_eofs", message=EOFDTO(data.operation_type, client,STATE_OK,"",amount_received_by_node,amount_sent_by_node).serialize())

    def send_eof_finish(self, data: EOFDTO):
        client = data.get_client()
        logging.debug(f"action: send_eof_finish | client: {client}")
        self.broker.public_message(sink=self.node_name + "_eofs", message=EOFDTO(data.operation_type, client,STATE_FINISH).serialize())

    def check_confirmations(self, data: EOFDTO):
        self.update_totals(data.client, data.get_amount_received(), data.get_amount_sent())   
        self.confirmations += 1
        logging.debug(f"action: check_confirmations | client: {data.get_client()} | confirmations: {self.confirmations}")
        if self.confirmations == self.amount_of_nodes:
            self.check_amounts(data)

    def check_amounts(self, data: EOFDTO):
        client = data.get_client()
        logging.debug(f"action: check_amounts | client: {client} | total_amount_received: {self.total_amount_received[client]} | expected_total_amount_received: {self.expected_total_amount_received[client]}")
        if self.total_amount_received[client] == self.expected_total_amount_received[client]:
            self.pre_eof_actions(client)
            self.send_eof(data)
            self.clients.remove(client)
            self.clients_pending_confirmations.remove(client)
            self.confirmations = 0
            self.reset_amounts(data)
            if self.amount_of_nodes > 1:
                self.send_eof_finish(data)
            return
        if self.amount_of_nodes < 2:
            raise PrematureEOFException()
        self.reset_totals(client)
        self.update_totals(client, self.amount_received_by_node[client], self.amount_sent_by_node[client])
        self.ask_confirmations(data)

    def process_node_eof(self, data: EOFDTO):
        logging.debug(f"action: process_node_eof | client: {data.client}")
        if data.client in self.clients_pending_confirmations:
            if data.is_ok():
                self.check_confirmations(data)
            return
        if data.is_ok():
            return
        if data.is_finish():
            self.reset_amounts(data)
            return
        if data.is_commit():
            self.pre_eof_actions(data.get_client())
            self.send_eof_confirmation(data)

    def update_totals(self, client, amount_received, amount_sent):
        self.update_total_amount_received(client, amount_received)
        self.update_total_amount_sent(client, amount_sent)

    def reset_totals(self, client):
        if client in self.total_amount_received:
            del self.total_amount_received[client]
        if client in self.total_amount_sent:
            del self.total_amount_sent[client]

    def reset_amounts(self,data: EOFDTO):
        client = data.get_client()
        if client in self.total_amount_received:
            del self.total_amount_received[client]
        if client in self.total_amount_sent:
            del self.total_amount_sent[client]
        if client in self.amount_received_by_node:
            del self.amount_received_by_node[client]
        if client in self.amount_sent_by_node:
            del self.amount_sent_by_node[client]
        if client in self.clients:
            self.clients.remove(client)

    def inform_eof_to_nodes(self, data: EOFDTO):
        client = data.get_client()
        logging.debug(f"action: inform_eof_to_nodes | client: {client}")
        self.reset_totals(client)
        self.update_totals(client, self.amount_received_by_node.get(client, 0), self.amount_sent_by_node.get(client, 0))
        self.expected_total_amount_received[client] = data.get_amount_sent()
        self.clients_pending_confirmations.append(client)
        if self.amount_of_nodes < 2:
            self.check_amounts(data)
            return
        self.ask_confirmations(data)

    def ask_confirmations(self, data: EOFDTO):
        self.confirmations = 1
        logging.debug(f"action: ask_confirmations | client: {data.get_client()} | pending_confirmations: {self.clients_pending_confirmations}")
        data.set_state(STATE_COMMIT)
        self.broker.public_message(sink=self.node_name + "_eofs", message=data.serialize())

    def read_nodes_eofs(self, ch, method, properties, body):
        try:
            data = DetectDTO(body).get_dto()
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
                self.inform_eof_to_nodes(data)
            else:
                self.check_new_client(data)
                self.process_data(data)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except UnfinishedGamesException as e:
            logging.debug(f"action: error | Unfinished Games Exception")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        except UnfinishedReviewsException as e:
            logging.debug(f"action: error | Unfinished Reviews Exception")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        except PrematureEOFException as e:
            logging.debug(f"action: error | Premature EOF Exception")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        except Exception as e:
            logging.error(f"action: error | result: {e}")

    def run(self):
        self.broker.start_consuming()
    
    def stop(self):
        self.broker.close()
    
    def pre_eof_actions(self, client_id):
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
