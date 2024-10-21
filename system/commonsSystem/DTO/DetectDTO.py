from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.EOFDTO import EOFDTO
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO
from system.commonsSystem.DTO.RawDTO import RawDTO
import logging
from typing import Union

class DetectDTO():
    def __init__(self, dto_in_bytes):
        self.dto_in_bytes = dto_in_bytes
        self.command_deserialize = {
            OperationType.OPERATION_TYPE_RAW: RawDTO,
            OperationType.OPERATION_TYPE_GAMES_DTO: GamesDTO,
            OperationType.OPERATION_TYPE_REVIEWS_DTO: ReviewsDTO,
            OperationType.OPERATION_TYPE_GAMES_EOF_DTO: EOFDTO,
            OperationType.OPERATION_TYPE_REVIEWS_EOF_DTO: EOFDTO,
        }

    def get_dto(self) -> Union[RawDTO, GamesDTO, ReviewsDTO, EOFDTO]:
        offset = 0
        operation_type = int.from_bytes(self.dto_in_bytes[offset:offset+1], byteorder='big')
        offset += 1
        if OperationType(operation_type) not in self.command_deserialize:
            logging.error(f"Unknown operation type: {operation_type}")
            logging.info(f"Operation types: {self.command_deserialize.keys()}")
            return None
        result, offset = self.command_deserialize[OperationType(operation_type)].deserialize(self.dto_in_bytes, offset)
        return result
    
