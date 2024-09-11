from socketTCP import SocketTCP
import logging

FORMAT_ENCODED = "utf-8"

class Protocol:
    
    def __init__(self, socket):
        self.socket = socket
    
    def send_number_1_byte(self, a_number):
        number_in_bytes = (a_number).to_bytes(1, byteorder='big')
        bytes_sent = 0 
        bytes_sent += self.socket.send_all(number_in_bytes)
        if bytes_sent != len(number_in_bytes):
            self.socket.close()
            raise RuntimeError(f"action: send_number_1_byte | result: fail | number: {a_number}")
    
    def recv_number_1_byte(self):
        number_in_bytes, bytes_recv = self.socket.recv_all(1)
        if bytes_recv != 1:
            self.socket.close()
            raise RuntimeError("action: recv_number_1_byte | result: fail |")
        number_int = int.from_bytes(number_in_bytes, byteorder='big') 
        return number_int 

    def send_number_2_bytes(self, a_number):
        number_in_bytes = (a_number).to_bytes(2, byteorder='big')
        bytes_sent = 0 
        bytes_sent += self.socket.send_all(number_in_bytes)
        if bytes_sent != len(number_in_bytes):
            self.socket.close()
            raise RuntimeError(f"action: send_number_2_byte | result: fail | number: {a_number}")
    
    def recv_number_2_bytes(self):
        number_in_bytes, bytes_recv = self.socket.recv_all(2)
        if bytes_recv != 2:
            self.socket.close()
            raise RuntimeError("action: recv_number_2_byte | result: fail |")
        number_int = int.from_bytes(number_in_bytes, byteorder='big') 
        return number_int 


    def send_string(self, a_string):
        bytes_sent = 0
        string_in_bytes = a_string.encode(FORMAT_ENCODED)
        size_string_bytes = len(string_in_bytes)
        
        self.send_number_2_bytes(size_string_bytes)
        bytes_sent += self.socket.send_all(string_in_bytes) 
        if bytes_sent != size_string_bytes:
            self.socket.close()
            raise RuntimeError(f"action: send_string | result: fail | string: {a_string} ")

    def recv_string(self):
        size_string_bytes = self.recv_number_2_bytes()
        str_in_bytes, bytes_recv = self.socket.recv_all(size_string_bytes) 
        if size_string_bytes != bytes_recv:
            self.socket.close()
            raise RuntimeError("action: recv_string | result: fail | ")
        string_decoded = str_in_bytes.decode(FORMAT_ENCODED)
        return string_decoded
        