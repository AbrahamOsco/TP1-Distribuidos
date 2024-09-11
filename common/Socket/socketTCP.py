import socket
import logging

class SocketTCP:

    def __init__(self, ip="", port=0, listen_backlog = 0, socket_peer=0):
        self.ip = ip
        self.was_closed = False
        self.port = port
        if (socket_peer != 0):
            self.socket = socket_peer
            return
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if (ip == ""):
            self.socket.bind(("", port))
            self.socket.listen(listen_backlog)
            self.listen_backlog = listen_backlog
    
    def accept(self):
        if (self.ip != ''):
            msg = "action: accept | result: fail | error: Socket is not a server socket"
            logging.error(msg)
            raise RuntimeError(msg)
        skt_peer, addr = self.socket.accept()
        socket_peer_object = SocketTCP(socket_peer=skt_peer, port=self.port)
        return socket_peer_object, addr
    
    def connect(self):
        if self.ip == '':
            msg = "action: connect | result: fail | error: Socket is not a client socket"
            logging.error(msg)
            return False, msg
        try:
            self.socket.settimeout(1)
            self.socket.connect((self.ip, self.port))
            self.socket.settimeout(None)
        except (OSError, ConnectionRefusedError) as e:
            return False, e
        return True, ""
    
    def close(self):
        self.socket.close()
        self.was_closed = self.socket._closed
    
    def is_closed(self) -> bool:
        return self.was_closed
    
    # si handleo el error deben cerrar el socket desde afuera
    def handler_error_send_all(self, total_bytes_sent, error=""):
        logging.error(f"{error}")
        return total_bytes_sent

    def send_all(self, a_object):
        total_bytes_sent = 0
        bytes_to_send = len(a_object)
        while total_bytes_sent < bytes_to_send:
            try:
                bytes_sent = self.socket.send(a_object[total_bytes_sent:]) # retorna la # de bytes enviados.
                if bytes_sent == 0:
                    return self.handler_error_send_all(total_bytes_sent, "action: send_all | result: fail | error: connection broken during send all!")
            except OSError as e:
                return self.handler_error_send_all(total_bytes_sent, f"action: send_all | result: fail | error: {e}")
            total_bytes_sent += bytes_sent
        return total_bytes_sent

    def handler_error_recv_all(self, bytes_received, error=""):
        logging.error(f"{error}")
        return b'', bytes_received
    
    def recv_all(self, total_bytes_to_receive):
        bytes_received = 0
        chunks = []
        while bytes_received < total_bytes_to_receive:
            try:
                chunk = self.socket.recv(total_bytes_to_receive - bytes_received) # retorna un objeto en bytes.
                if chunk == b'':
                    return self.handler_error_recv_all(bytes_received, "action: recv_all | result: fail | error: connection broken during recv all!")
            except OSError as e:
                    return self.handler_error_recv_all(bytes_received, f"action: send_all | result: fail | error: {e}")
            chunks.append(chunk)
            bytes_received += len(chunk)
        return b''.join(chunks), bytes_received

    def get_peer_name(self):
        return self.socket.getpeername()
        
