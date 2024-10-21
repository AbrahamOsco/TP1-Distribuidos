from system.commonsSystem.DTO.DTO import DTO
from system.commonsSystem.DTO.enums.OperationType import OperationType
from common.DTO.GameEOFDTO import OPERATION_TYPE_GAMEEOF
from common.DTO.GamesRawDTO import OPERATION_TYPE_GAMES_RAW
from common.DTO.ReviewsRawDTO import OPERATION_TYPE_REVIEWS_RAW
from common.DTO.ReviewEOFDTO import OPERATION_TYPE_REVIEWEOF


class RawDTO(DTO):
    def __init__(self, client_id:int=0, type:int=0, raw_data=[], batch_id=0, global_counter=0):
        self.operation_type = OperationType.OPERATION_TYPE_RAW
        self.client_id = client_id
        self.type = type
        self.raw_data = raw_data
        self.batch_id = batch_id
        self.global_counter = global_counter

    def serialize(self):
        raw_bytes = bytearray()
        raw_bytes.extend(self.operation_type.value.to_bytes(1, byteorder='big'))
        raw_bytes.extend(self.client_id.to_bytes(1, byteorder='big'))
        raw_bytes.extend(self.type.to_bytes(1, byteorder='big'))
        raw_bytes.extend(self.global_counter.to_bytes(6, byteorder='big'))
        raw_bytes.extend(len(self.raw_data).to_bytes(2, byteorder='big'))
        raw_bytes.extend(self.batch_id.to_bytes(2, byteorder='big'))
        for element in self.raw_data:
            raw_bytes.extend(len(element).to_bytes(2, byteorder='big'))
            for field in element:
                raw_bytes.extend(DTO.serialize_str(field))
        return bytes(raw_bytes)

    def deserialize(data, offset):
        client_id = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        global_counter = int.from_bytes(data[offset:offset+6], byteorder='big')
        offset += 6
        raw_data = []
        items_amount = int.from_bytes(data[offset:offset+2], byteorder='big')
        offset += 2
        batch_id = int.from_bytes(data[offset:offset+2], byteorder='big')
        offset += 2
        for _ in range(items_amount):
            element = []
            field_amount = int.from_bytes(data[offset:offset+2], byteorder='big')
            offset += 2
            for _ in range(field_amount):
                field, offset = DTO.deserialize_str(data, offset)
                element.append(field)
            raw_data.append(element)
        return RawDTO(client_id=client_id, type=type, raw_data=raw_data, batch_id=batch_id, global_counter=global_counter), offset
    
    def set_counter(self, counter):
        self.global_counter = counter

    def is_EOF(self):
        return self.type == OPERATION_TYPE_GAMEEOF or self.type == OPERATION_TYPE_REVIEWEOF
    
    def is_games_EOF(self):
        return self.type == OPERATION_TYPE_GAMEEOF
    
    def is_reviews_EOF(self):
        return self.type == OPERATION_TYPE_REVIEWEOF
    
    def is_reviews(self):
        return self.type == OPERATION_TYPE_REVIEWS_RAW
    
    def is_games(self):
        return self.type == OPERATION_TYPE_GAMES_RAW
    
    def get_client(self):
        return self.client_id