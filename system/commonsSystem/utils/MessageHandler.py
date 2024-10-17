from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.DetectDTO import DetectDTO

class MessageHandler:
    def __init__(self):
        pass

    @classmethod
    def with_eof(cls, handler_eof, function_to_apply):
        def handler_message(ch, method, properties, body):
            result_dto = DetectDTO(body).get_dto()
            if result_dto.operation_type == OperationType.OPERATION_TYPE_EOF_DTO:
                handler_eof.init_leader_and_push_eof(result_dto)  
            else:
                function_to_apply(result_dto)
            ch.basic_ack(delivery_tag =method.delivery_tag)
        return handler_message

