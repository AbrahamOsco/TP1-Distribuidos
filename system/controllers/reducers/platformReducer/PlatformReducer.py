from system.commonsSystem.DTO.enums.OperationType import OperationType
from common.utils.utils import initialize_log
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.DTO.PlatformDTO import PlatformDTO
import os
import logging
import signal

QUEUE_PLATFORMCOUNTER_REDUCER = "platformCounter_platformReducer"
QUEUE_RESULTQ1_GATEWAY = "platformResultq1_gateway"

class PlatformReducer:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.broker = Broker()
        self.registered_client = False
        signal.signal(signal.SIGTERM, self.handler_sigterm)
        self.total_platform = PlatformDTO()
        self.broker.create_queue(name =QUEUE_PLATFORMCOUNTER_REDUCER, durable =True, callback=self.handler_callback_exchange())
        self.broker.create_queue(name =QUEUE_RESULTQ1_GATEWAY, durable =True)
    
    def handler_callback_exchange(self):
        def handler_message(ch, method, properties, body):
            result = DetectDTO(body).get_dto()
            if result.operation_type != OperationType.OPERATION_TYPE_PLATFORM_DTO:
                # Here! recien we send the PlatformDTO by exchange !! 
                logging.info(f"TODO: HANDLER: EOF 🔚 🏮 🗡️")
            logging.info(f" Result: {result} {result.operation_type} {result.operation_type.value}")
            self.count_all_platforms(result)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_message

    def count_all_platforms(self, platformDTO: PlatformDTO):
        if not self.registered_client:
            self.total_platform.client_id = platformDTO.client_id
            self.registered_client = True
        self.total_platform.windows += platformDTO.windows
        self.total_platform.linux += platformDTO.linux
        self.total_platform.mac += platformDTO.mac
        logging.info(f"action: Total reducer current 🤯 💯 Windows: {self.total_platform.windows} Linux: {self.total_platform.linux}"\
                     f"Mac: {self.total_platform.mac} | success: ✅ ")
        self.broker.public_message(queue_name =QUEUE_RESULTQ1_GATEWAY, message =self.total_platform.serialize())

    def handler_sigterm(self, signum, frame):
        logging.info(f"action:⚡signal SIGTERM {signum} was received | result: sucess ✅ ")
        self.broker.close()

    def run(self):
        self.broker.start_consuming()
        logging.info("action: Initialize PlatformReducer 🦅 | success: ✅")

