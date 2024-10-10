from system.commonsSystem.utils.serialize import serialize_str, deserialize_str

class SerializerReviewsInitial:
    
    def __init__(self):
        pass

    def serialize(self, resultQuery, monitor_bytes):
        for app_id, name_and_reviewlist in resultQuery.data.items():
            monitor_bytes.extend(app_id.to_bytes(8, byteorder='big')) #es el id
            monitor_bytes.extend(serialize_str(name_and_reviewlist[0])) # pos 0es el nombre del game.
            monitor_bytes.extend(len(name_and_reviewlist[1]).to_bytes(4, byteorder='big')) # pos 1 es una lista con el texto de cada review.
            for a_text in name_and_reviewlist[1]:
                monitor_bytes.extend(serialize_str(a_text))
        return bytes(monitor_bytes)

    def deserialize(self, data, offset, client_id, dic_length):
        from system.commonsSystem.DTO.ResultQueryDTO import ResultQueryDTO
        data_result_dic = {}
        for _ in range(dic_length):
            app_id = int.from_bytes(data[offset:offset+8], byteorder='big')
            offset += 8
            name, offset = deserialize_str(data, offset)
            size_list_reviews = int.from_bytes(data[offset:offset+4], byteorder='big')
            offset += 4
            list_reviews = []
            for _ in range(size_list_reviews):
                review, offset = deserialize_str(data, offset)
                list_reviews.append(review)
            data_result_dic[app_id] = [name, list_reviews]

        return ResultQueryDTO(client_id =client_id, data =data_result_dic)

