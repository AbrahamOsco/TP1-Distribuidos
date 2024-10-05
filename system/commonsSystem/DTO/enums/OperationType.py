from enum import Enum

class OperationType(Enum):
    OPERATION_TYPE_RAW = 0
    OPERATION_TYPE_GAMES_DTO = 1
    OPERATION_TYPE_REVIEWS_DTO = 2
    OPERATION_TYPE_GAMES_EOF_DTO = 3
    OPERATION_TYPE_REVIEWS_EOF_DTO = 4
    OPERATION_TYPE_REVIEWED_GAME_DTO = 8
    OPERATION_TYPE_STR = 27
    
