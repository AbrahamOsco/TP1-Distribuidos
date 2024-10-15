from common.socket.Socket import Socket

FORMAT_ENCODED = "utf-8"

class Protocol:
    
    def __init__(self, socket: Socket):
        self.socket = socket

    def stop(self):
        self.socket.close()
    
    def send_number_n_bytes(self, n, a_number):
        number_in_bytes = (a_number).to_bytes(n, byteorder='big')
        self.socket.sendall(number_in_bytes)
    
    def recv_number_n_bytes(self, n):
        number_in_bytes, bytes_recv = self.socket.recv_all(n)
        if bytes_recv != n:
            self.socket.close()
            raise RuntimeError("action: recv_number_1_byte | result: fail |")
        number_int = int.from_bytes(number_in_bytes, byteorder='big') 
        return number_int

    def recv_number_n_bytes_timeout(self, n):
        number_in_bytes, bytes_recv = self.socket.recv_all_timeout(n)
        if bytes_recv != n:
            self.socket.close()
            raise RuntimeError("action: recv_number_1_byte | result: fail |")
        number_int = int.from_bytes(number_in_bytes, byteorder='big') 
        return number_int

    def send_string(self, a_string):
        string_in_bytes = a_string.encode(FORMAT_ENCODED)
        size_string_bytes = len(string_in_bytes)
        
        self.send_number_n_bytes(3, size_string_bytes)
        self.socket.sendall(string_in_bytes)

    def recv_string(self):
        size_string_bytes = self.recv_number_n_bytes(3)
        str_in_bytes, bytes_recv = self.socket.recv_all(size_string_bytes) 
        if size_string_bytes != bytes_recv:
            self.socket.close()
            raise RuntimeError("action: recv_string | result: fail | ")
        string_decoded = str_in_bytes.decode(FORMAT_ENCODED)
        return string_decoded
    
    