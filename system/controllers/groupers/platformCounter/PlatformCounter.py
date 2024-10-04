from system.commonsSystem.DTO.enums.OperationType import OperationType
from common.utils.utils import initialize_log
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_PLATFORM
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.DetectDTO import DetectDTO
import os
import logging
from system.commonsSystem.DTO.PlatformDTO import PlatformDTO

QUEUE_SELECTQ1_PLATFORMCOUNTER = "selectq1_platformCounter"
QUEUE_PLATFORMCOUNTER_REDUCER = "platformCounter_platformReducer"

class PlatformCounter:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.platform = PlatformDTO()
        self.registered_client = False
        self.broker = Broker()
        self.count_baches = 0 #borrar esto es de prueba debe tenerminar ucando sea EOF pero lo hago para q llege a 3 y mande al reducer
        self.broker.create_queue(name =QUEUE_SELECTQ1_PLATFORMCOUNTER, durable =True, callback =self.handler_callback())
        self.broker.create_queue(name=QUEUE_PLATFORMCOUNTER_REDUCER, durable =True)
        # Exchange del lado del producer, solo crea el exchange y luego publica mensajes                      

    def handler_callback(self):
        def handler_message(ch, method, properties, body):
            result = DetectDTO(body).get_dto()
            if result.operation_type != OperationType.OPERATION_TYPE_GAMES_DTO:
                logging.info(f"TODO: HANDLER: EOF 🔚 🏮 🗡️")  
            logging.info(f" Result: {result} {result.operation_type} {result.operation_type.value}")
            self.count_platforms(result)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_message

    def count_platforms(self, gamesDTO:GamesDTO):
        if not self.registered_client:
            self.platform.client_id = gamesDTO.client_id
            self.registered_client = True
        for a_game in gamesDTO.games_dto:
            self.platform.windows += a_game.windows
            self.platform.linux += a_game.linux
            self.platform.mac += a_game.mac
        logging.info(f"action: Amount of platforms 🕹️🐕 🔥  Window:{self.platform.windows}"\
                     f"Linux:{self.platform.linux} Mac:{self.platform.mac} | success: ✅")
        self.count_baches +=1
        if self.count_baches == 3:
            self.broker.public_message(queue_name =QUEUE_PLATFORMCOUNTER_REDUCER, message =self.platform.serialize())

    def run(self):
        self.broker.start_consuming()
        # self.broker.close() # Solo hacer el close cuando recibamos la signal y acabe todo ordenado!!. 



