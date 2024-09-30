from system.commonsSystem.broker.Queue import Queue
from common.utils.utils import initialize_log 
from system.commonsSystem.broker.BrokerSerializer import BrokerSerializer
import logging
import pika

class Broker:

    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        self.channel = self.connection.channel()
        initialize_log(logging_level='INFO')
        self.queues = {}
        self.broker_serializer = BrokerSerializer()

    def create_queue(self, name ='', durable =False, callback =None):
        a_queue = Queue(name =name, durable =durable, callback =callback)
        result = self.channel.queue_declare(queue =name, durable =durable, exclusive =a_queue.get_exclusive())
        a_queue.set_name(result.method.queue)
        self.queues[a_queue.get_name()] = a_queue
        if callback != None:
            self.channel.basic_consume(queue =a_queue.get_name(), auto_ack =False, on_message_callback =callback)
        a_queue.show_status()
        return a_queue.get_name()

    # Connect a exchange with a queue with a binding!. La binding key es la 'key' de la queue. 
    # if the routing key del mensaje coincicide con la binding key,esta queue recibira el mensaje. 
    def bind_queue(self, exchange_name, queue_name, binding_key = None):
        self.queues[queue_name].set_binding_key(binding_key)
        self.channel.queue_bind(exchange =exchange_name, queue =queue_name, routing_key =binding_key)
        logging.info(f"action: Binding queue: {queue_name} to exchange: {exchange_name} | result: sucess ✅")

    # Necesita el nombre del exchange y el nombre de la queue, el binding key ya se lo guarda no necesitas pasarlo.
    def unbind_queue(self, exchange_name, queue_name):
        self.channel.queue_unbind(exchange =exchange_name, queue =queue_name, routing_key =self.queues[queue_name].get_binding_key())
        
    #Se debe crear el exchange de ambos lados (productor y consumidor) 
    def create_exchange(self, exchange_type, name=''):
        logging.info(f"action: Created a Exchange: | name: {name} | type: {exchange_type} | result: sucess ✅")
        self.channel.exchange_declare(exchange =name, exchange_type =exchange_type)

    # Si no especificamos el queue_name (casi siempre haremos esto), mandamos por el exchange con su routing_key definido. 
    def public_message(self, exchange_name='', queue_name='', routing_key='', message=''):
        message = self.broker_serializer.serialize(message)
        if queue_name != '':
            self.channel.basic_publish(exchange =exchange_name, routing_key =queue_name, body=message,\
                properties = self.queues[queue_name].get_properties())
        else:
            # Todos los mensajes q se publican a un exchange seran persistentes! existira. Habra alguna situacion que no queramos esto 
            # con mandatory = true Hace que el mensaje no se pierda si no hay colas vinculadas. Al inicio puede q la queue todavia no exista
            # pero el exchange si y con este 'mandatory' el mensaje no se perdera!.
            self.channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=message,\
                                       properties=pika.BasicProperties(delivery_mode=2))

    def get_message(self, message):
        return self.broker_serializer.deserialize(message)


    def start_consuming(self):
        self.channel.start_consuming()

    def close(self):
        self.connection.close()

    def enable_worker_queues(self):
        self.channel.basic_qos(prefetch_count=1)
