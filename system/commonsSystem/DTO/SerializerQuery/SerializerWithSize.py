from system.commonsSystem.utils.serialize import serialize_str, deserialize_str

class SerializerWithSize:
    
    def __init__(self):
        pass

    def serialize(self, resultQuery, monitor_bytes):
        monitor_bytes.extend(resultQuery.size_games.to_bytes(8, byteorder='big')) # Envio la cantidad de games en total. para q sepa el total.
        for app_id, name_and_count in resultQuery.data.items():
            monitor_bytes.extend(app_id.to_bytes(8, byteorder='big')) #es el id
            monitor_bytes.extend(serialize_str(name_and_count[0])) # pos 0es el nombre del game.
            monitor_bytes.extend(name_and_count[1].to_bytes(4, byteorder='big')) # pos 1 es una lista con el texto de cada review.
        return bytes(monitor_bytes)

    def deserialize(self, data, offset, client_id, dic_length):
        from system.commonsSystem.DTO.ResultQueryDTO import ResultQueryDTO
        data_result_dic = {}
        size_games = int.from_bytes(data[offset:offset+8], byteorder='big')
        offset += 8
        for _ in range(dic_length):
            app_id = int.from_bytes(data[offset:offset+8], byteorder='big')
            offset += 8
            name, offset = deserialize_str(data, offset)
            count = int.from_bytes(data[offset:offset+8], byteorder='big')
            offset += 8
            data_result_dic[app_id] = (name, count)
                        
        return ResultQueryDTO(client_id =client_id, data =data_result_dic, size_games = size_games)
