import logging
import os
import signal
import sys
import threading
import time
from system.commonsSystem.node.healthcheck import HealthcheckServer, start_healthcheck_server, shutdown_server
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.EOFDTO import EOFDTO, STATE_COMMIT
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.node.EOFManagement import EOFManagement
from system.commonsSystem.node.routingPolicies.RoutingPolicy import RoutingPolicy
from system.commonsSystem.node.routingPolicies.RoutingDefault import RoutingDefault

class Node:
    def __init__(self, routing: RoutingPolicy = RoutingDefault()):
        self.initialize_config()
        self.node_name = os.getenv("NODE_NAME")
        self.node_id = os.getenv("NODE_ID")
        self.source = os.getenv("SOURCE").split(',')
        self.source_name = os.getenv("SOURCE_NAME", self.node_name)
        self.source_key = os.getenv("SOURCE_KEY", "default").split(',')
        self.source_type = os.getenv("SOURCE_TYPE", "direct").split(',')
        self.sink = os.getenv("SINK")
        self.sink_type = os.getenv("SINK_TYPE", "direct")
        self.amount_of_nodes = int(os.getenv("AMOUNT_OF_NODES", 1))
        self.clients_pending_confirmations = {}
        self.running = True
        self.eof_controller = None
        self.confirmations_lock = threading.Lock()
        self.confirmations = {}
        self.eof = EOFManagement(routing)
        self.broker = Broker()
        self.initialize_queues()
        self.initialize_healthcheck()

    def initialize_healthcheck(self):
        self.healthcheck_server = HealthcheckServer()
        self.healthcheck_thread = threading.Thread(target=start_healthcheck_server, args=(self.healthcheck_server,))
        self.healthcheck_thread.start()

    def initialize_queues(self):
        ## Source and destination for all workers
        for i, source in enumerate(self.source):
            if i >= len(self.source_key) or i >= len(self.source_type):
                raise ValueError("Mismatched list sizes: source, source_key, and source_type must have the same length")
            self.broker.create_source(name=self.source_name, callback=self.process_queue_message)
            self.broker.create_sink(type=self.source_type[i], name=source)
            self.broker.bind_queue(queue_name=self.source_name, sink=source, routing_key=self.source_key[i])
        self.broker.create_sink(type=self.sink_type, name=self.sink)
        if self.amount_of_nodes < 2:
            return
        ## Fanout for EOFs
        eof_queue = self.broker.create_source(callback=self.read_nodes_eofs)
        self.broker.create_sink(type="fanout", name=self.node_name + "_eofs")
        self.broker.bind_queue(queue_name=eof_queue, sink=self.node_name + "_eofs")
        self.eof_controller = threading.Thread(target=self.check_eofs, args=())
        self.eof_controller.start()

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

    def resend_eof_to_brothers(self, data: EOFDTO):
        temporal_broker = Broker("temporal")
        self.ask_confirmations(temporal_broker, data, 1)
        temporal_broker.close()

    def check_eofs(self):
        while self.running:
            time.sleep(0.5)
            with self.confirmations_lock:
                for client in list(self.clients_pending_confirmations.keys()):
                    information = self.clients_pending_confirmations[client]
                    if information[3] == 1 and time.time() - information[0] > 7:
                        logging.error("action: check_eofs | result: timeout")
                        del self.clients_pending_confirmations[client]
                        continue
                    if information[3] == 0 and time.time() - information[0] > 4:
                        logging.error("action: check_eofs | result: resend")
                        self.clients_pending_confirmations[client] = (time.time(), information[1], information[2], 1)
                        self.resend_eof_to_brothers(information[2])

    def send_eof(self, data: EOFDTO):
        client = data.get_client()
        eofs = self.eof.get_eof_for_next_node(data)
        for message, routing_key in eofs:
            logging.info(f"action: send_eof | client: {client} | routing_key: {routing_key}")
            self.broker.public_message(sink=self.sink, message=message.serialize(), routing_key=routing_key)

    def send_eof_confirmation(self, data: EOFDTO):
        message = self.eof.get_eof_confirmation(data)
        self.broker.public_message(sink=self.node_name + "_eofs", message=message.serialize())

    def send_eof_cancel(self, data: EOFDTO):
        message = self.eof.get_eof_cancel(data)
        self.broker.public_message(sink=self.node_name + "_eofs", message=message.serialize())

    def check_confirmations(self, data: EOFDTO):
        client = data.get_client() 
        self.confirmations[client] += 1
        logging.debug(f"action: check_confirmations | client: {client} | confirmations: {self.confirmations}")
        if self.confirmations[client] == self.amount_of_nodes:
            self.check_amounts(data)

    def check_cancel(self, data: EOFDTO):
        client = data.get_client()
        information = self.clients_pending_confirmations[client]
        self.broker.basic_nack(information[1])
        del self.clients_pending_confirmations[client]

    def check_amounts(self, data: EOFDTO):
        client = data.get_client()
        self.pre_eof_actions(client)
        self.send_eof(data)
        if client in self.clients_pending_confirmations:
            self.broker.basic_ack(self.clients_pending_confirmations[client][1])
            del self.clients_pending_confirmations[client]
        if client in self.confirmations:
            del self.confirmations[client]

    def ask_confirmations(self, broker: Broker, data: EOFDTO, retry:int = 0):
        client = data.get_client()
        self.confirmations[client] = 1
        logging.debug(f"action: ask_confirmations | client: {client} | pending_confirmations: {self.clients_pending_confirmations}")
        message = EOFDTO(data.operation_type, client, STATE_COMMIT, global_counter=data.global_counter, retry=retry)
        broker.public_message(sink=self.node_name + "_eofs", message=message.serialize())

    def no_older_message(self, data: EOFDTO):
        eof_global_counter = data.global_counter
        message = self.broker.peek(self.source_name)
        if message is None:
            return True
        last_message = DetectDTO(message).get_dto()
        return last_message.global_counter > eof_global_counter

    def process_commit(self, data: EOFDTO):
        if self.no_older_message(data):
            self.pre_eof_actions(data.get_client())
            self.send_eof_confirmation(data)
            return
        self.send_eof_cancel(data)

    def process_node_eof(self, data: EOFDTO):
        client = data.get_client()
        logging.info(f"action: process_node_eof | client: {client}")
        with self.confirmations_lock:
            if client in self.clients_pending_confirmations:
                if data.is_cancel():
                    self.check_cancel(data)
                if data.retry != self.clients_pending_confirmations[client][3]:
                    return
                if data.is_ok():
                    self.check_confirmations(data)
                return
        if data.is_ok():
            return
        if data.is_commit():
            self.process_commit(data)

    def inform_eof_to_nodes(self, data: EOFDTO, delivery_tag: str):
        client = data.get_client()
        logging.info(f"action: inform_eof_to_nodes | client: {client}")
        self.clients_pending_confirmations[client] = (time.time(), delivery_tag, data, 0)
        if self.amount_of_nodes < 2:
            self.check_amounts(data)
            return
        with self.confirmations_lock:
            self.ask_confirmations(self.broker, data)

    def read_nodes_eofs(self, ch, method, properties, body):
        try:
            data = DetectDTO(body).get_dto()
            self.process_node_eof(data)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logging.error(f"action: eof queue error | result: {e}")

    def process_queue_message(self, ch, method, properties, body):
        # try:
            data = DetectDTO(body).get_dto()
            if data.is_EOF():
                self.inform_eof_to_nodes(data, method.delivery_tag)
            else:
                self.process_data(data)
                ch.basic_ack(delivery_tag=method.delivery_tag)
        # except Exception as e:
        #     logging.error(f"action: data queue error | result: {e}")
        #     ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def run(self):
        signal.signal(signal.SIGTERM, lambda _n,_f: self.stop())
        self.broker.start_consuming()
    
    def stop(self):
        self.running = False
        self.broker.close()
        if self.eof_controller is not None:
            self.eof_controller.join()
        shutdown_server(self.healthcheck_server)
        self.healthcheck_thread.join()
        sys.exit(0)
    
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
