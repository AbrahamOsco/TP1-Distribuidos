import logging
from system.commonsSystem.DTO.DecadeDTO import DecadeDTO
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_GAMES_INITIAL, STATE_PLATFORM
from system.commonsSystem.DTO.GameDTO import GameDTO
from system.commonsSystem.DTO.GenreDTO import GenreDTO
from system.commonsSystem.DTO.PlatformDTO import PlatformDTO
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.GamesIndexDTO import GamesIndexDTO
from system.commonsSystem.DTO.ReviewsIndexDTO import ReviewsIndexDTO
from system.commonsSystem.DTO.EOFDTO import EOFDTO

class DetectDTO:
    def __init__(self, dto_in_bytes):
        self.dto_in_bytes = dto_in_bytes
        self.command_deserialize = {
            #OperationType.OPERATION_TYPE_GAME: GameDTO(),
            OperationType.OPERATION_TYPE_GAMES_DTO: GamesDTO(client_id =0, state_games =0),
            OperationType.OPERATION_TYPE_PLATFORM_DTO: PlatformDTO(),
            OperationType.OPERATION_TYPE_GENRE_DTO: GenreDTO(),
            OperationType.OPERATION_TYPE_DECADE_DTO: DecadeDTO(),
            OperationType.OPERATION_TYPE_GAMES_INDEX_DTO: GamesIndexDTO(),
            OperationType.OPERATION_TYPE_REVIEWS_INDEX_DTO: ReviewsIndexDTO(),
            OperationType.OPERATION_TYPE_EOF_INITIAL: EOFDTO(),
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
    

