from common.socket.Socket import Socket
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.broker.Broker import Broker
from common.utils.utils import initialize_log, ResultType
from system.commonsSystem.protocol.ServerProtocol import ServerProtocol
from system.commonsSystem.DTO.EOFDTO import EOFDTO
from system.controllers.gateway.RawHandler import RawHandler
import signal
import logging
import os

QUEUE_RESULTQ1_GATEWAY = "resultq1_gateway"
QUEUE_RESULTQ2_GATEWAY = "resultq2_gateway"
QUEUE_RESULTQ3_GATEWAY = "resultq3_gateway"
QUEUE_RESULTQ4_GATEWAY = "resultq4_gateway"
QUEUE_RESULTQ5_GATEWAY = "resultq5_gateway"

PORT_GATEWAY = 12345

class Gateway:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.socket_accepter = Socket(port =PORT_GATEWAY)
        self.there_was_sigterm = False
        signal.signal(signal.SIGTERM, self.handler_sigterm)
        self.broker = Broker()
        self.broker.create_queue(name =QUEUE_RESULTQ1_GATEWAY, callback= self.recv_result_query(ResultType.RESULT_QUERY_1))
        self.broker.create_queue(name =QUEUE_RESULTQ2_GATEWAY, callback= self.recv_result_query(ResultType.RESULT_QUERY_2))
        self.broker.create_queue(name =QUEUE_RESULTQ3_GATEWAY, callback= self.recv_result_query(ResultType.RESULT_QUERY_3))
        self.broker.create_queue(name =QUEUE_RESULTQ4_GATEWAY, callback= self.recv_result_query(ResultType.RESULT_QUERY_4))
        self.broker.create_queue(name =QUEUE_RESULTQ5_GATEWAY, callback= self.recv_result_query(ResultType.RESULT_QUERY_5))
        self.raw_handler = RawHandler()
    
    def recv_result_query(self, result_type):
        def handler_query_result(ch, method, properties, body):
            result = DetectDTO(body).get_dto()
            logging.info(f"Action: Gateway Recv Result: {result_type} 🕹️ success: ✅")
            self.protocol.send_result_query(result, result_type)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_query_result
    

    def accept_a_connection(self):
        logging.info("action: Waiting a client to connect | result: pending ⌚")
        self.socket_peer, addr = self.socket_accepter.accept()
        logging.info("action: Waiting a client to connect | result: success ✅")
        self.protocol = ServerProtocol(self.socket_peer)
    
    def run(self):
        try:
            self.accept_a_connection()
            self.raw_handler.start(self.protocol)
            self.broker.start_consuming()
        except Exception as e:
            if self.there_was_sigterm == False:
                logging.error(f"action: Handling a error | result: error ❌ | error: {e}")
        finally:
            self.free_all_resource()
            logging.info("action: Release all resource | result: success ✅")

    def free_all_resource(self):
        self.raw_handler.close()
        self.socket_peer.close()
        self.socket_accepter.close()
        self.broker.close()
    
    def handler_sigterm(self, signum, frame):
        self.there_was_sigterm = True
        self.free_all_resource()

