import logging
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.DTO.GameDTO import GameDTO
from system.commonsSystem.DTO.PlatformDTO import PlatformDTO
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.GamesIndexDTO import GamesIndexDTO
from system.commonsSystem.DTO.ReviewsIndexDTO import ReviewsIndexDTO
from system.commonsSystem.DTO.EOFDTO import EOFDTO
from system.commonsSystem.DTO.CalculatorDTO import CalculatorDTO
from system.commonsSystem.DTO.DataPartialDTO import DataPartialDTO
from system.commonsSystem.DTO.TopDTO import TopDTO
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO
from system.commonsSystem.DTO.ResultQueryDTO import ResultQueryDTO

class DetectDTO:
    def __init__(self, dto_in_bytes):
        self.dto_in_bytes = dto_in_bytes
        self.command_deserialize = {
            OperationType.OPERATION_TYPE_GAMES_DTO: GamesDTO(),
            OperationType.OPERATION_TYPE_PLATFORM_DTO: PlatformDTO(),
            OperationType.OPERATION_TYPE_GAMES_INDEX_DTO: GamesIndexDTO(),
            OperationType.OPERATION_TYPE_REVIEWS_INDEX_DTO: ReviewsIndexDTO(),
            OperationType.OPERATION_TYPE_EOF_DTO: EOFDTO(),
            OperationType.OPERATION_TYPE_CALCULATOR_DTO: CalculatorDTO(),
            OperationType.OPERATION_TYPE_DATA_PARTIAL_DTO: DataPartialDTO(),
            OperationType.OPERATION_TYPE_TOP_DTO: TopDTO(),
            OperationType.OPERATION_TYPE_REVIEWS_DTO: ReviewsDTO(),
            OperationType.OPERATION_TYPE_RESULT_QUERY_DTO: ResultQueryDTO(),
        }

    def get_dto(self):
        offset = 0
        #Primer byte indica el tipo de operacion, usando Command, obtenemos el dto a usar!. 
        operation_type = int.from_bytes(self.dto_in_bytes[offset:offset+1], byteorder='big')
        try:
            result = self.command_deserialize[OperationType(operation_type)].deserialize(self.dto_in_bytes, offset)
        except KeyError:
            logging.error(f"Unknown operation type: {operation_type}")
        return result
    

