from common.utils.utils import initialize_log
import logging
import pika

# TODO: Broker debe vivir en el system y no en common por ahora lo hago para hacer bien la api luego hay que moverlo
class Broker:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        self.channel = self.connection.channel()
        initialize_log(logging_level='INFO')

    # el create_queue es idempotente puede ejecutarlo muchas veces y solo uno sera creado
    # good practice repetir la queue no sabemos si el producer o consumer corre uno antes q otro. 
    def create_queue(self, queue_name=''):
        self.channel.queue_declare(queue=queue_name)
    
    # con pasarle un queue_name y un message es suficiente para enviar un n mensaje 
    def public_message(self, exchange_name='', queue_name='', routing_key='', message=''):
        if queue_name != '':
            self.channel.basic_publish(exchange=exchange_name, routing_key=queue_name, body=message)
            logging.info(f"action: publish a message: {message} 🍍")
        elif queue_name == '':
            self.channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=message)
    
    def assign_callback(self, call_back, queue_name=''):
        self.channel.basic_consume(queue=queue_name, auto_ack= False, on_message_callback =call_back)
        pass

    def start_consuming(self):
        self.channel.start_consuming()

    def close(self):
        self.connection.close()
    
