from system.commonsSystem.broker.Queue import Queue
from common.utils.utils import initialize_log 
import logging
import pika
import sys

HEARTBEAT = 5000

class Broker:

    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', heartbeat =HEARTBEAT ))
        self.channel = self.connection.channel()
        initialize_log(logging_level='INFO')
        self.queues = {}
        self.was_closed = False
        self.enable_worker_queues() 
    
    def create_queue(self, name='', durable=True, callback=None):
        try:
            a_queue = Queue(name=name, durable=durable, callback=callback)
            result = self.channel.queue_declare(queue=name, durable=durable, exclusive=a_queue.get_exclusive())
            a_queue.set_name(result.method.queue)
            self.queues[a_queue.get_name()] = a_queue
            if callback is not None:
                self.channel.basic_consume(queue=a_queue.get_name(), auto_ack=False, on_message_callback=callback)
            return a_queue.get_name()
        except Exception as e:
            logging.error(f"Failed to create queue {name}: {e}")
            raise

    # Connect a exchange with a queue with a binding!. La binding key es la 'key' de la queue. 
    # if the routing key del mensaje coincicide con la binding key,esta queue recibira el mensaje. 
    def bind_queue(self, exchange_name, queue_name, binding_key = None):
        self.queues[queue_name].set_binding_key(binding_key)
        self.channel.queue_bind(exchange =exchange_name, queue =queue_name, routing_key =binding_key)

    # Necesita el nombre del exchange y el nombre de la queue, el binding key ya se lo guarda no necesitas pasarlo.
    def unbind_queue(self, exchange_name, queue_name):
        self.channel.queue_unbind(exchange =exchange_name, queue =queue_name, routing_key =self.queues[queue_name].get_binding_key())
        
    #Se debe crear el exchange de ambos lados (productor y consumidor) 3 exchange_types: 'direct', 'fanout', 'topic'
    def create_exchange(self, exchange_type, name=''):
        self.channel.exchange_declare(exchange =name, exchange_type =exchange_type)
    
    def create_fanout_and_bind(self, name_exchange ="", callback =None):
        self.create_exchange(name =name_exchange, exchange_type='fanout')
        name_anonymous_queue = self.create_queue(callback =callback)
        self.bind_queue(exchange_name =name_exchange, queue_name =name_anonymous_queue)    

    # Si no especificamos el queue_name es una queue anonyma mandamos por el exchange con su routing_key definido.
    # Si especifciamos el name es una working queue y ultiples workers deben estar conectadas a esta hacer.  
    def public_message(self, exchange_name='', queue_name='', routing_key='', message=''):
        if queue_name != '':
            self.channel.basic_publish(exchange =exchange_name, routing_key =queue_name, body=message,
                properties = self.queues[queue_name].get_properties())
        else:
            # Todos los mensajes q se publican a un exchange seran persistentes! existira. Habra alguna situacion que no queramos esto??
            # El mensaje pusheado a un exchange se pierde, si no existen ningna queue bindeada al exchange! ⏰ 
            self.channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=message,
                                       properties=pika.BasicProperties(delivery_mode=2))

    def start_consuming(self):
        try:
            self.channel.start_consuming()
        except Exception as e:
            if self.was_closed == False:
                logging.error(f" action: Handling a error {e} | result: success ✅")
            self.close()


    def close(self):
        if self.was_closed:
            return 
        self.channel.stop_consuming()
        logging.info("action: Stopping consuming from RabbitMQ queues | result: success ✅")
        self.channel.close()
        logging.info("action: Closing RabbitMQ channel | result: success ✅")
        self.connection.close()
        logging.info("action: Closing RabbitMQ connection | result: success ✅")
        self.was_closed = True

    def enable_worker_queues(self):
        self.channel.basic_qos(prefetch_count=1)
