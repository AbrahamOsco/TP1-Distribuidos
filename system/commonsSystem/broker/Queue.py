import logging
import pika

class Queue:
    def __init__(self, name, durable, callback):
        self.command_properties = {False : None, True : pika.BasicProperties(\
                                delivery_mode = pika.DeliveryMode.Persistent)}
        self.exclusive = False
        self.callback = callback
        self.name = name
        if (self.name == ''):
            self.exclusive = True # la queue se eliminara al cerrar el channel.
        self.durable = durable
        self.properties = pika.BasicProperties(delivery_mode= pika.DeliveryMode.Persistent,)  # make message persistent (quiero persistir el mensaje)
        self.routing_key = ''
        self.consumer_tag = ''

    def set_name(self, name):
        self.name = name
    
    def set_consumer_tag(self, consumer_tag):
        self.consumer_tag = consumer_tag

    def set_binding_key(self, binding_key):
        self.binding_key = binding_key

    def get_binding_key(self):
        return self.binding_key

    def get_name(self):
        return self.name

    def get_properties(self):
        return self.properties

    def get_exclusive(self):
        return self.exclusive

