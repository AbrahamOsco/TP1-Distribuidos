from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.DTO.enums.OperationType import OperationType
import logging

class DetectDTO():
    def __init__(self, dto_in_bytes):
        self.dto_in_bytes = dto_in_bytes
        self.command_deserialize = {
            OperationType.OPERATION_TYPE_GAMES_DTO: GamesDTO(),
        }

    def get_dto(self):
        offset = 0
        operation_type = int.from_bytes(self.dto_in_bytes[offset:offset+1], byteorder='big')
        offset += 1
        try:
            result, offset = self.command_deserialize[OperationType(operation_type)].deserialize(self.dto_in_bytes, offset)
        except KeyError:
            logging.error(f"Unknown operation type: {operation_type}")
        return result
    
