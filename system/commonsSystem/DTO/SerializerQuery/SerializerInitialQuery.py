from system.commonsSystem.utils.serialize import serialize_str, deserialize_str

class SerializerInitialQuery:
    
    def __init__(self):
        pass

    def serialize(self, resultQuery, monitor_bytes):
        for key, value in resultQuery.data.items():
            monitor_bytes.extend(key.to_bytes(8, byteorder='big'))
            monitor_bytes.extend(serialize_str(value[0]))
            monitor_bytes.extend(value[1].to_bytes(8, byteorder='big'))
        return bytes(monitor_bytes)

    def deserialize(self, data, offset, client_id, dic_length):
        from system.commonsSystem.DTO.ResultQueryDTO import ResultQueryDTO
        data_result_dic = {}
        for _ in range(dic_length):
            app_id = int.from_bytes(data[offset:offset+8], byteorder='big')
            offset += 8
            name, offset = deserialize_str(data, offset)
            score = int.from_bytes(data[offset:offset+8], byteorder='big')
            offset += 8
            data_result_dic[app_id] = [name, score]

        return ResultQueryDTO(client_id =client_id, data =data_result_dic)

