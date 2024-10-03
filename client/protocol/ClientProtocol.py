from common.protocol.Protocol import Protocol

class ClientProtocol(Protocol):
    
    def __init__(self, a_id, socket):
        self.id = a_id
        super().__init__(socket)  #uso super para invocar al constructor del padre. 

# [ ["1", "3", "abcasda", "1", "0"], ["2", "4", "abc", "-1", "0"], ... ] 
    def send_data_raw(self, data_raw_dto):
        self.send_number_1_byte(data_raw_dto.operation_type)
        self.send_number_1_byte(data_raw_dto.client_id) 
        self.send_number_2_bytes(len(data_raw_dto.data_raw))
        for item in data_raw_dto.data_raw:
            self.send_number_2_bytes(len(item))
            for field in item:
                self.send_string(field)

    def recv_platform_q1(self):
        operation_type = self.recv_number_1_byte()
        client_id = self.recv_number_1_byte()
        windows = self.recv_number_4_bytes()
        linux = self.recv_number_4_bytes()
        mac = self.recv_number_4_bytes()
        return {"ClientID": client_id,
                "Windows": windows, "Linux": linux, "Mac": mac}
        