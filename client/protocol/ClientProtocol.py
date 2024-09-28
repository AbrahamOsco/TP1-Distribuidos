import logging
from common.protocol.Protocol import Protocol, OPERATION_GAME_RAW, OPERATION_REVIEW_RAW

class ClientProtocol(Protocol):
    
    def __init__(self, a_id, socket):
        self.id = a_id
        super().__init__(socket)  #uso super para invocar al constructor del padre. 

# [ [1, 3, "abcasda", 1, 0], [2, 4, "abc", -1, 0], ... ] 
# Recibe una lista de lista itera cada lista interna y envia cada string q contiene cada una. 
    def send_data_raw(self, operation_type,  list_items_raw):
        self.send_number_1_byte(self.id)
        self.send_number_1_byte(operation_type)
        items_amount = len(list_items_raw)
        self.send_number_2_bytes(items_amount)
        for element in list_items_raw:
            field_amount = len(element)
            self.send_number_2_bytes(field_amount)
            for field in element:
                self.send_string(field)
    

