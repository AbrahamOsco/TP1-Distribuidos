import logging
from system.commonsSystem.DTO.DetectDTO import DetectDTO

def eof_calculator(handler_eof):
    def handler_message(ch, method, properties, body):
        result_dto = DetectDTO(body).get_dto()
        handler_eof.run(calculatorDTO =result_dto)
        ch.basic_ack(delivery_tag =method.delivery_tag)
    return handler_message

def handler_sigterm_default(broker):
    def handler_sigterm(signum, frame):
        logging.info(f"action:⚡signal SIGTERM {signum} was received | result: sucess ✅ ")
        broker.close()
    return handler_sigterm