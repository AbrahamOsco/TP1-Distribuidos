from common.protocol.Protocol import Protocol, OPERATION_GAME_RAW, OPERATION_REVIEW_RAW

class ServerProtocol(Protocol):
    
    def __init__(self, socket):
        super().__init__(socket)  #uso super para invocar al constructor del padre. 

    def recv_data_raw(self):
        client_id = self.recv_number_1_byte()
        operation_type = self.recv_number_1_byte()
        list_items_raw = []
        items_amount = self.recv_number_2_bytes()
        for i in range(items_amount):
            element = []
            field_amount = self.recv_number_2_bytes()
            for j in range(field_amount):
                field = self.recv_string()
                element.append(field)
            list_items_raw.append(element)
        return client_id, operation_type, list_items_raw
    
