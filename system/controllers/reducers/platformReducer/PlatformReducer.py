from system.commonsSystem.DTO.enums.OperationType import OperationType
from common.utils.utils import initialize_log
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.DetectDTO import DetectDTO
import os
import logging
from system.commonsSystem.DTO.PlatformDTO import PlatformDTO

EXCHANGE_PLATFORMCOUNTER_REDUCER = "exchange_platformCounter_platformReducer"
ROUTING_KEY_PLATFORMCOUNTER = "platformCounter.platformReducer"

EXCHANGE_RESULTQ1_GATEWAY = "platformReducer_gateway"
ROUTING_KEY_RESULT_QUERY_1 = "result.query.1"

class PlatformReducer:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.broker = Broker()
        self.registered_client = False
        self.total_platform = PlatformDTO()
        # Exchange del lado del consumer hace un bind_queue /tiene un bindingkey para filtrar los mensajes. 
        self.broker.create_exchange_and_bind(name_exchange=EXCHANGE_PLATFORMCOUNTER_REDUCER,
                                    binding_key =ROUTING_KEY_PLATFORMCOUNTER, callback =self.handler_callback_exchange())
        #Exchange del lado del producer solo crea el exchange.
        self.broker.create_exchange(name = EXCHANGE_RESULTQ1_GATEWAY, exchange_type='direct')

    
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
        self.broker.public_message(exchange_name =EXCHANGE_RESULTQ1_GATEWAY, routing_key =ROUTING_KEY_RESULT_QUERY_1,
                                    message =self.total_platform.serialize())
    def run(self):
        self.broker.start_consuming()
        logging.info("action: Initialize PlatformReducer 🦅 | success: ✅")
        # self.broker.close() # Solo hacer el close cuando recibamos la signal y acabe todo ordenado!!. 

