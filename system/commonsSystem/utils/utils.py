import logging
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.DTO.enums.OperationType import OperationType

DIC_GAME_FEATURES_TO_USE = {"AppID": 0 , "Name": 0, "Windows": 0, "Mac": 0, "Linux": 0,
                            "Genres": 0, "Release date": 0, "Average playtime forever": 0}
DIC_REVIEW_FEATURES_TO_USE = { 'app_id':0, 'review_text':0, 'review_score':0 }                              


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
