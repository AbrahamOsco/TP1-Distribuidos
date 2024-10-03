from common.protocol.Protocol import Protocol
from common.utils.utils import ResultType

class ClientProtocol(Protocol):

    def __init__(self, a_id, socket):
        self.id = a_id
        super().__init__(socket)  #uso super para invocar al constructor del padre.
        self.command_result_query = {
            ResultType.RESULT_QUERY_1.value: self.recv_result_query_1,
            ResultType.RESULT_QUERY_2.value: self.recv_result_query_2,
            ResultType.RESULT_QUERY_3.value: self.recv_result_query_3,
            ResultType.RESULT_QUERY_4.value: self.recv_result_query_4,
            ResultType.RESULT_QUERY_5.value: self.recv_result_query_5,
        }

    def send_data_raw(self, data_raw_dto):
        self.send_number_1_byte(data_raw_dto.operation_type)
        self.send_number_1_byte(data_raw_dto.client_id)
        self.send_number_2_bytes(len(data_raw_dto.data_raw))
        for item in data_raw_dto.data_raw:
            self.send_number_2_bytes(len(item))
            for field in item:
                self.send_string(field)
    
    def recv_result_query(self):
        result_type = self.recv_number_1_byte()
        return self.command_result_query[result_type]()

    def recv_result_query_1(self):
        client_id = self.recv_number_1_byte()
        windows = self.recv_number_4_bytes()
        linux = self.recv_number_4_bytes()
        mac = self.recv_number_4_bytes()
        return {"ResultType":ResultType.RESULT_QUERY_1, "ClientID": client_id,
                "Windows": windows, "Linux": linux, "Mac": mac}

    def recv_result_query_2(self):
        pass

    def recv_result_query_3(self):
        pass

    def recv_result_query_4(self):
        pass
    
    def recv_result_query_5(self):
        pass
