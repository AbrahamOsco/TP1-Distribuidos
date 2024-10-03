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
        self.broker.create_queue(name =QUEUE_PLATFORMCOUNTER_REDUCER, durable =True)

    
    def run(self):
        self.broker.start_consuming()
        logging.info("action: Initialize PlatformReducer 🦅 | success: ✅")
        # self.broker.close() # Solo hacer el close cuando recibamos la signal y acabe todo ordenado!!. 

