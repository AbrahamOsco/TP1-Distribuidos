from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.utils.serialize import serialize_str, deserialize_str
from system.commonsSystem.DTO.SerializerQuery.SerializerFinalQuery import SerializerFinalQuery
from system.commonsSystem.DTO.SerializerQuery.SerializerInitialQuery import SerializerInitialQuery
from system.commonsSystem.DTO.SerializerQuery.SerializerReviewsInitial import SerializerReviewsInitial
from system.commonsSystem.DTO.SerializerQuery.SerializerWithSize import SerializerWithSize


RESULT_INITIAL = 1
RESULT_TOP = 2
RESULT_REVIEWS_INITIAL = 3
RESULT_WIHT_SIZE = 4

class ResultQueryDTO:
    def __init__(self, client_id: int = 0, data ={}, status =RESULT_INITIAL, size_games = 0):
        self.operation_type = OperationType.OPERATION_TYPE_RESULT_QUERY_DTO
        self.client_id = client_id
        self.data = data
        self.size_games = size_games
        self.status = status
        self.command_result = {RESULT_INITIAL: SerializerInitialQuery(),
                             RESULT_TOP: SerializerFinalQuery(), 
                             RESULT_REVIEWS_INITIAL: SerializerReviewsInitial(),
                            RESULT_WIHT_SIZE: SerializerWithSize(),
        }

    def serialize(self):
        result_bytes = bytearray()
        result_bytes.extend(self.operation_type.value.to_bytes(1, byteorder='big'))
        result_bytes.extend(self.status.to_bytes(1, byteorder='big'))
        result_bytes.extend(self.client_id.to_bytes(1, byteorder='big'))
        result_bytes.extend(len(self.data).to_bytes(2, byteorder='big'))
        return self.command_result[self.status].serialize(self, result_bytes)

    def deserialize(self, data, offset):
        operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        status = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        self.status = status
        
        client_id = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        
        dic_length = int.from_bytes(data[offset:offset+2], byteorder='big')
        offset += 2
        return self.command_result[self.status].deserialize(data, offset, client_id, dic_length)
   