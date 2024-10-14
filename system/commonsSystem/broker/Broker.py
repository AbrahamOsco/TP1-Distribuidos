import pika.exceptions
from system.commonsSystem.broker.Queue import Queue
from common.utils.utils import initialize_log 
import logging
import pika
import time
import socket
import sys

class Broker:

    def __init__(self, tag=""):
        self.tag = tag
        self.stablish_connection()
        initialize_log(logging_level='INFO')
        self.queues = {}
        self.enable_worker_queues() # Toda queue con name sera una working queue! 👈

    def stablish_connection(self, retries=5):
        delay = 4
        for attempt in range(retries):
            try:
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                    'rabbitmq',
                    heartbeat=600,
                    tcp_options={"TCP_KEEPIDLE": 60, "TCP_KEEPINTVL": 10, "TCP_KEEPCNT": 5}
                ))
                self.channel = self.connection.channel()
                return
            except socket.gaierror as e:
                print(f"Attempt {attempt + 1} failed with error: {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2
            except pika.exceptions.AMQPConnectionError as e:
                print(f"Attempt {attempt + 1} failed with error: {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2
        raise Exception("Failed to establish connection after multiple retries.")

    def create_source(self, name ='', callback =None):
        durable = name != ''
        a_queue = Queue(name =name, durable =durable, callback =callback)
        result = self.channel.queue_declare(queue =name, durable =durable, exclusive =a_queue.get_exclusive())
        a_queue.set_name(result.method.queue)
        self.queues[a_queue.get_name()] = a_queue
        if callback != None:
            self.channel.basic_consume(queue =a_queue.get_name(), auto_ack =False, on_message_callback =callback)
        a_queue.show_status()
        return a_queue.get_name()

    def create_sink(self, type, name=''):
        logging.info(f"action: Created a Exchange: | name: {name} | type: {type} | result: sucess ✅")
        self.channel.exchange_declare(exchange=name, exchange_type=type)

    def bind_queue(self, queue_name='', sink='', routing_key='default'):
        self.channel.queue_bind(exchange=sink, queue=queue_name, routing_key=routing_key)

    def public_message(self, sink='', routing_key='default', message=''):
        self.channel.basic_publish(exchange=sink, routing_key=routing_key, body=message,
                                    properties=pika.BasicProperties(delivery_mode=2))

    def start_consuming(self):
        try:
            self.channel.start_consuming()
        except Exception as e:
            sys.exit(-1)
        logging.info(f"action: start_consuming {self.tag} | result: finished ✅")

    def close(self):
        try:
            logging.info(f"action: stop consuming {self.tag} | result: pending ⌚")
            self.channel.stop_consuming()
            logging.info(f"action: stop consuming {self.tag}| result: success ✅")
            self.connection.close()
        except Exception as e:
            logging.info(f"action: close | result: failed ❌ | error: {e}")

    def enable_worker_queues(self):
        self.channel.basic_qos(prefetch_count=1)

    def get_message(self, body):
        return body.decode()