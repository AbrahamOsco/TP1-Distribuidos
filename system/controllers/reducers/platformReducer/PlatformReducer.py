from system.commonsSystem.DTO.enums.OperationType import OperationType
from common.utils.utils import initialize_log
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.DTO.PlatformDTO import PlatformDTO
from system.commonsSystem.utils.utils import handler_sigterm_default
import os
import logging
import signal

QUEUE_PLATFORMCOUNTER_REDUCER = "platformCounter_platformReducer"
QUEUE_RESULTQ1_GATEWAY = "resultq1_gateway"

class PlatformReducer:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.broker = Broker()
        self.registered_client = False
        signal.signal(signal.SIGTERM, handler_sigterm_default(self.broker))
        
        self.total_platform = PlatformDTO()
        self.broker.create_queue(name =QUEUE_PLATFORMCOUNTER_REDUCER, callback=self.handler_callback_exchange())
        self.broker.create_queue(name =QUEUE_RESULTQ1_GATEWAY)
    
    def handler_callback_exchange(self):
        def handler_message(ch, method, properties, body):
            result_dto = DetectDTO(body).get_dto()
            if result_dto.operation_type == OperationType.OPERATION_TYPE_EOF_DTO:
                self.broker.public_message(queue_name =QUEUE_RESULTQ1_GATEWAY, message =self.total_platform.serialize())
            else:
                self.count_all_platforms(result_dto)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_message

    def count_all_platforms(self, platformDTO: PlatformDTO):
        if not self.registered_client:
            self.total_platform.client_id = platformDTO.client_id
            self.registered_client = True
        self.total_platform.windows += platformDTO.windows
        self.total_platform.linux += platformDTO.linux
        self.total_platform.mac += platformDTO.mac

    def run(self):
        self.broker.start_consuming()

