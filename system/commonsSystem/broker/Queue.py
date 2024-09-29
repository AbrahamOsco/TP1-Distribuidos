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
        self.properties = self.command_properties[self.durable]
        self.routing_key = ''

    def set_name(self, name):
        self.name = name
    
    def set_binding_key(self, binding_key):
        self.binding_key = binding_key

    def get_binding_key(self):
        return self.binding_key

    def get_name(self):
        return self.name

    def show_status(self):
        has_callback = "✅"
        if self.callback == None:
            has_callback = "⛔"
        logging.info(f"action: Created a Queue: | name: {self.name} | durable: {self.durable} | exclusive: {self.exclusive}"\
                     f"| call_back: {has_callback} | result: sucess ✅")

    def get_properties(self):
        return self.properties

    def get_exclusive(self):
        return self.exclusive

