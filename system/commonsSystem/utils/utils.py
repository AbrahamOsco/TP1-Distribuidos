import logging
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.DTO.enums.OperationType import OperationType

DIC_GAME_FEATURES_TO_USE = {0:"app_id" , 1:"name", 2:"release_date", 17: "windows", 18: "mac", 19: "linux", 29: "avg_playtime_forever", 36: "genres"}
DIC_REVIEW_FEATURES_TO_USE = {0:'app_id', 2:'review_text', 3:'review_score'}


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
