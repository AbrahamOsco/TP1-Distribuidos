from system.commonsSystem.DTO.DTO import DTO
from system.commonsSystem.DTO.enums.OperationType import OperationType
from common.DTO.GameEOFDTO import OPERATION_TYPE_GAMEEOF
from common.DTO.GamesRawDTO import OPERATION_TYPE_GAMES_RAW
from common.DTO.ReviewsRawDTO import OPERATION_TYPE_REVIEWS_RAW
from common.DTO.ReviewEOFDTO import OPERATION_TYPE_REVIEWEOF


class RawDTO(DTO):
    def __init__(self, client_id:int=0, type:int=0, raw_data=[]):
        self.operation_type = OperationType.OPERATION_TYPE_RAW
        self.client_id = client_id
        self.type = type
        self.raw_data = raw_data

    def serialize(self):
        raw_bytes = bytearray()
        raw_bytes.extend(self.operation_type.value.to_bytes(1, byteorder='big'))
        raw_bytes.extend(self.client_id.to_bytes(1, byteorder='big'))
        raw_bytes.extend(self.type.to_bytes(1, byteorder='big'))
        raw_bytes.extend(len(self.raw_data).to_bytes(2, byteorder='big'))
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
        raw_data = []
        items_amount = int.from_bytes(data[offset:offset+2], byteorder='big')
        offset += 2
        for _ in range(items_amount):
            element = []
            field_amount = int.from_bytes(data[offset:offset+2], byteorder='big')
            offset += 2
            for _ in range(field_amount):
                field, offset = DTO.deserialize_str(data, offset)
                element.append(field)
            raw_data.append(element)
        return RawDTO(client_id=client_id, type=type, raw_data=raw_data), offset

    def is_EOF(self):
        return False
    
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