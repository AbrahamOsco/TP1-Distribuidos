import logging
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.utils.serialize import serialize_str, deserialize_str

class TopDTO:

    def __init__(self, client_id = 0, results={}):
        self.operation_type = OperationType.OPERATION_TYPE_TOP_DTO
        self.client_id = client_id
        self.results = results

    def serialize(self):
        result_bytes = bytearray()
        result_bytes.extend(self.operation_type.value.to_bytes(1, byteorder='big'))
        result_bytes.extend(self.client_id.to_bytes(1, byteorder='big'))
        result_bytes.extend(len(self.results).to_bytes(1, byteorder='big'))
        for key, value in self.results.items():
            result_bytes.extend(serialize_str(key))
            result_bytes.extend(value.to_bytes(4, byteorder='big'))
        return bytes(result_bytes)

    def deserialize(self, data, offset):
        operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        client_id = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        size_result = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        results = {}
        for i in range(size_result):
            name, offset = deserialize_str(data, offset)
            amount = int.from_bytes(data[offset:offset+4], byteorder='big')
            offset += 4
            results[name] = amount
        return TopDTO(client_id= client_id, results = results)
