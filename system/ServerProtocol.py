from common.protocol.Protocol import Protocol

class ServerProtocol(Protocol):
    
    def __init__(self, socket):
        super().__init__(socket)  #uso super para invocar al constructor del padre. 

    def recv_data_raw(self):
        list_items_raw = []
        items_amount = self.recv_number_2_bytes()
        for i in range(items_amount):
            element = []
            field_amount = self.recv_number_2_bytes()
            for j in range(field_amount):
                field = self.recv_string()
                element.append(field)
            list_items_raw.append(element)
        return list_items_raw
    
    def send_data_raw(self, list_items_raw):
        items_amount = len(list_items_raw)
        self.send_number_2_bytes(items_amount)
        for element in list_items_raw:
            field_amount = len(element)
            self.send_number_2_bytes(field_amount)
            for field in element:
                self.send_string(field)
        
                


            
