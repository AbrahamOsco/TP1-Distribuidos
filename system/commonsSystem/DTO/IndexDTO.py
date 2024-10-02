from system.commonsSystem.DTO.DTO import DTO

class IndexDTO(DTO):
    def __init__(self, client_id =0, data_raw = [], indexes = {} ):
        self.client_id = client_id
        self.indexes = indexes
        self.data_raw = data_raw
    
    def serialize(self):
        index_bytes = bytearray()
        index_bytes.extend(self.operation_type.value.to_bytes(1, byteorder='big'))
        index_bytes.extend(self.client_id.to_bytes(1, byteorder='big'))
        
        index_bytes.extend(len(self.data_raw).to_bytes(2, byteorder='big'))
        for element in self.data_raw:
            index_bytes.extend(len(element).to_bytes(2, byteorder='big'))
            for field in element:
                index_bytes.extend(self.serialize_str(field))

        index_bytes.extend(len(self.indexes).to_bytes(1, byteorder='big'))
        for name, index in self.indexes.items():
            index_bytes.extend(self.serialize_str(name))
            index_bytes.extend(index.to_bytes(1, byteorder='big'))
        return bytes(index_bytes)

    def deserialize(self, data, offset = 0):
        operation_type = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        client_id = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1

        items_raw_length = int.from_bytes(data[offset:offset+2], byteorder='big')
        offset += 2
        items_raw = []
        for i in range(items_raw_length):
            a_item_length = int.from_bytes(data[offset:offset+2], byteorder='big')
            offset += 2
            a_item = []
            for j in range(a_item_length):
                field, offset = self.deserialize_str(data, offset)
                a_item.append(field)
            items_raw.append(a_item)

        indexes_length = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        indexes = {}
        for i in range(indexes_length):
            name, offset = self.deserialize_str(data, offset)
            index = int.from_bytes(data[offset:offset+1], byteorder='big')
            offset += 1
            indexes[name] = index
        # pattern Template method! 🔥
        return self.get_instance(client_id, indexes, items_raw, offset)
    
    def get_instance(self, client_id, indexes, items_raw, offset):
        pass
