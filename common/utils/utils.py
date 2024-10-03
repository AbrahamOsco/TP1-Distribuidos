import logging
from enum import Enum

class ResultType(Enum):
    RESULT_QUERY_1 = 1
    RESULT_QUERY_2 = 2
    RESULT_QUERY_3 = 3
    RESULT_QUERY_4 = 4
    RESULT_QUERY_5 = 5

def initialize_log(logging_level):
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging_level,
        datefmt='%Y-%m-%d %H:%M:%S',
    )

