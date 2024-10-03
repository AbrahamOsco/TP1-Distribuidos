from system.commonsSystem.DTO.enums.OperationType import OperationType
from common.utils.utils import initialize_log
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.DetectDTO import DetectDTO
import os
import logging
from system.commonsSystem.DTO.PlatformDTO import PlatformDTO

QUEUE_PLATFORMCOUNTER_REDUCER = "platformCounter_platformReducer"

class PlatformReducer:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.broker = Broker()
        self.platform = PlatformDTO()
        self.broker.create_queue(name =QUEUE_PLATFORMCOUNTER_REDUCER, durable =True, callback =self.handler_callback())

    def handler_callback(self):
        def handler_message(ch, method, properties, body):
            result = DetectDTO(body).get_dto()
            if result.operation_type != OperationType.OPERATION_TYPE_PLATFORM_DTO:
                logging.info(f"TODO: HANDLER: EOF 🔚 🏮 🗡️")  
            logging.info(f" Result: {result} {result.operation_type} {result.operation_type.value}")
            self.count_platforms(result)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_message

    def count_all_platforms(self, platformDTO: PlatformDTO):
        if not self.registered_counter:
            self.platform.client_id = platformDTO.client_id
            self.registered_counter = True
        self.platform.windows += platformDTO.windows
        self.platform.linux += platformDTO.linux
        self.platform.mac += platformDTO.mac
        
    def run(self):
        self.broker.start_consuming()
        logging.info("action: Initialize PlatformReducer 🦅 | success: ✅")
        # self.broker.close() # Solo hacer el close cuando recibamos la signal y acabe todo ordenado!!. 

