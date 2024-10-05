from common.protocol.Protocol import Protocol
from common.DTO.GameEOFDTO import OPERATION_TYPE_GAMEEOF
from common.DTO.ReviewEOFDTO import OPERATION_TYPE_REVIEWEOF
from system.commonsSystem.DTO.RawDTO import RawDTO

class ServerProtocol(Protocol):
    
    def __init__(self, socket):
        super().__init__(socket)  #uso super para invocar al constructor del padre. 

    def recv_data_raw(self):
        operation_type = self.recv_number_1_byte()
        client_id = self.recv_number_1_byte()
        if operation_type == OPERATION_TYPE_GAMEEOF or operation_type == OPERATION_TYPE_REVIEWEOF:
            return RawDTO(client_id =client_id, type =operation_type, raw_data =[])
        list_items_raw = []
        items_amount = self.recv_number_2_bytes()
        for _ in range(items_amount):
            element = []
            field_amount = self.recv_number_2_bytes()
            for _ in range(field_amount):
                field = self.recv_string()
                element.append(field)
            list_items_raw.append(element)
        return RawDTO(client_id =client_id, type=operation_type, raw_data =list_items_raw)
