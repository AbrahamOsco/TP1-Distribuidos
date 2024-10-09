from common.protocol.Protocol import Protocol
from common.utils.utils import ResultType

class ClientProtocol(Protocol):

    def __init__(self, a_id, socket):
        self.id = a_id
        super().__init__(socket)  #uso super para invocar al constructor del padre.
        self.command_result_query = {
            ResultType.RESULT_QUERY_1.value: self.recv_result_query_1,
            ResultType.RESULT_QUERY_2.value: self.recv_result_top,
            ResultType.RESULT_QUERY_3.value: self.recv_result_top,
            ResultType.RESULT_QUERY_4.value: self.recv_result_top,
            ResultType.RESULT_QUERY_5.value: self.recv_result_top,
        }

    def send_data_raw(self, data_raw_dto):
        self.send_number_1_byte(data_raw_dto.operation_type)
        self.send_number_1_byte(data_raw_dto.client_id)
        self.send_number_4_bytes(len(data_raw_dto.data_raw))
        for item in data_raw_dto.data_raw:
            self.send_number_2_bytes(len(item))
            for field in item:
                self.send_string(field)
    
    def recv_result_query(self):
        result_type = self.recv_number_1_byte()
        result_dic = {}
        result_dic["result_type"] = result_type
        return self.command_result_query[result_type](result_type, result_dic)

    def recv_result_query_1(self, result_type, result_dic):
        client_id = self.recv_number_1_byte()
        windows = self.recv_number_4_bytes()
        linux = self.recv_number_4_bytes()
        mac = self.recv_number_4_bytes()
        result_dic["Windows"] = windows
        result_dic["Linux"] = linux
        result_dic["Mac"] = mac
        return result_dic

    def recv_result_top(self, result_type, result_dic):
        client_id = self.recv_number_1_byte()
        size_results = self.recv_number_2_bytes()
        top_games = {}
        for i in range(size_results):
            name_game = self.recv_string()
            score = self.recv_number_4_bytes()
            top_games[name_game] = score
        result_dic["client_id"] = client_id
        result_dic["games"] = [top_games]
        return result_dic

    def send_eof(self, type_file_finish, client_id):
        self.send_number_1_byte(type_file_finish)
        self.send_number_1_byte(client_id)
    