from system.controllers.gateway.GlobalCounter import GlobalCounter
from system.commonsSystem.DTO.GamesDTO import GamesDTO

MAX_CLIENTS=10

class GatewayStructure():
    def to_bytes(result_eofs_by_client, last_batch_by_client, responses_by_client, client_allows):
        structure_bytes = bytearray()
        structure_bytes.extend(GlobalCounter.get_current().to_bytes(6, byteorder='big'))
        structure_bytes.extend(len(result_eofs_by_client).to_bytes(1, byteorder='big'))
        for client_id, result_eofs in result_eofs_by_client.items():
            structure_bytes.extend(client_id.to_bytes(1, byteorder='big'))
            structure_bytes.extend(len(result_eofs).to_bytes(2, byteorder='big'))
            for result_eof in result_eofs:
                structure_bytes.extend(result_eof.to_bytes(1, byteorder='big'))
        structure_bytes.extend(len(last_batch_by_client).to_bytes(1, byteorder='big'))
        for client_id, last_batch in last_batch_by_client.items():
            structure_bytes.extend(client_id.to_bytes(1, byteorder='big'))
            structure_bytes.extend(last_batch.to_bytes(2, byteorder='big'))
        structure_bytes.extend(len(responses_by_client).to_bytes(1, byteorder='big'))
        for client_id, response in responses_by_client.items():
            structure_bytes.extend(client_id.to_bytes(1, byteorder='big'))
            structure_bytes.extend(len(response).to_bytes(2, byteorder='big'))
            for response in response:
                structure_bytes.extend(response.serialize())
        for client_allow in client_allows:
            structure_bytes.extend(client_allow.to_bytes(1, byteorder='big'))
        return bytes(structure_bytes)
    
    def from_bytes(data):
        offset = 0
        if len(data) == 0:
            return {}, {}, {}, [True]*MAX_CLIENTS
        global_counter = int.from_bytes(data[offset:offset+6], byteorder='big')
        offset += 6
        result_eofs_by_client = {}
        result_eofs_by_client_length = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        for _ in range(result_eofs_by_client_length):
            client_id = int.from_bytes(data[offset:offset+1], byteorder='big')
            offset += 1
            result_eofs = set()
            result_eofs_length = int.from_bytes(data[offset:offset+2], byteorder='big')
            offset += 2
            for _ in range(result_eofs_length):
                result_eofs.add(int.from_bytes(data[offset:offset+1], byteorder='big'))
                offset += 1
            result_eofs_by_client[client_id] = result_eofs
        last_batch_by_client = {}
        last_batch_by_client_length = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        for _ in range(last_batch_by_client_length):
            client_id = int.from_bytes(data[offset:offset+1], byteorder='big')
            offset += 1
            last_batch = int.from_bytes(data[offset:offset+2], byteorder='big')
            offset += 2
            last_batch_by_client[client_id] = last_batch
        responses_by_client = {}
        responses_by_client_length = int.from_bytes(data[offset:offset+1], byteorder='big')
        offset += 1
        for _ in range(responses_by_client_length):
            client_id = int.from_bytes(data[offset:offset+1], byteorder='big')
            offset += 1
            responses = []
            responses_length = int.from_bytes(data[offset:offset+2], byteorder='big')
            offset += 2
            for _ in range(responses_length):
                offset += 1
                response, offset = GamesDTO.deserialize(data, offset)
                responses.append(response)
            responses_by_client[client_id] = responses
        client_allows = []
        for _ in range(MAX_CLIENTS):
            client_allows.append(bool.from_bytes(data[offset:offset+1], byteorder='big'))
            offset += 1
        GlobalCounter.set_current(global_counter)
        return result_eofs_by_client, last_batch_by_client, responses_by_client, client_allows