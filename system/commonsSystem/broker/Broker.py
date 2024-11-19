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
                logging.getLogger("pika").setLevel(logging.ERROR)
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

    def restablish_channel(self):
        self.channel = self.connection.channel()
        for queue in self.queues.values():
            name = queue.name
            if not queue.durable:
                name = ""
            result = self.channel.queue_declare(queue =name, durable =queue.durable, exclusive=queue.get_exclusive())
            queue.set_name(result.method.queue)
            self.channel.basic_consume(queue=queue.name, auto_ack=False, on_message_callback=queue.callback)
            self.channel.queue_bind(exchange=queue.sink, queue=queue.name, routing_key=queue.routing_key)

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
        logging.debug(f"action: Created a Exchange: | name: {name} | type: {type} | result: sucess ✅")
        self.channel.exchange_declare(exchange=name, exchange_type=type)

    def bind_queue(self, queue_name='', sink='', routing_key='default'):
        self.queues[queue_name].set_sink(sink, routing_key)
        self.channel.queue_bind(exchange=sink, queue=queue_name, routing_key=routing_key)

    def public_message(self, sink='', routing_key='default', message=''):
        self.channel.basic_publish(exchange=sink, routing_key=routing_key, body=message,
                                    properties=pika.BasicProperties(delivery_mode=2))

    def basic_nack(self, delivery_tag):
        self.channel.basic_nack(delivery_tag=delivery_tag, requeue=True)

    def basic_ack(self, delivery_tag):
        self.channel.basic_ack(delivery_tag=delivery_tag)

    def start_consuming(self):
        try:
            self.channel.start_consuming()
        except pika.exceptions.ChannelClosedByBroker as e:
            logging.warning(f"Channel closed by broker: {e}. Attempting to recreate channel.")
            self.restablish_channel()
            self.start_consuming()
        except Exception as e:
            logging.error(f"Irrecuperable error: {e}")
            sys.exit(-1)
        logging.info(f"action: start_consuming {self.tag} | result: finished ✅")

    def peek(self, queue_name):
        method_frame, header_frame, next_message = self.channel.basic_get(queue_name)

        if method_frame:
            self.channel.basic_nack(method_frame.delivery_tag, requeue=True)
            return next_message
        return None

    def close(self):
        try:
            logging.info(f"action: stop consuming {self.tag} | result: pending ⌚")
            self.channel.stop_consuming()
            self.connection.close()
            logging.info(f"action: stop consuming {self.tag}| result: success ✅")
        except Exception as e:
            logging.info(f"action: close | result: failed ❌ | error: {e}")
#
    def enable_worker_queues(self):
        self.channel.basic_qos(prefetch_count=1)

    def get_message(self, body):
        return body.decode()