from enum import Enum

class OperationType(Enum):
    OPERATION_TYPE_RAW = 0
    OPERATION_TYPE_GAMES_DTO = 1
    OPERATION_TYPE_REVIEWS_DTO = 2
    OPERATION_TYPE_GAMES_EOF_DTO = 3
    OPERATION_TYPE_REVIEWS_EOF_DTO = 4
    OPERATION_TYPE_SHORT_STR = 27
    OPERATION_TYPE_MID_STR = 28
    OPERATION_TYPE_LONG_STR = 29
    
