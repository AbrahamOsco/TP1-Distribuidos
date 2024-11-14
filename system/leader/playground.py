import socket
import socket
import logging
import threading
import time
MAX_LISTEN_BACKLOG = 30

class Socket:

    def __init__(self, ip="", port=0, socket_peer=0):
        self.ip = ip
        self.was_closed = False
        self.port = port
        if (socket_peer != 0):
            self.socket = socket_peer
            return
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if (ip == ""):
            self.socket.bind(("", port))
            self.socket.listen(MAX_LISTEN_BACKLOG)
    
    def accept_simple(self):
        if (self.ip != ""):
            msg = "action: accept | result: fail | error: Socket is not a server socket"
            logging.error(msg)
            raise RuntimeError(msg)
        try:
            skt_peer, addr = self.socket.accept()
            return Socket(socket_peer=skt_peer, port =self.port), addr
        except OSError as e:
            return None, e


    def accept(self):
        if (self.ip != ""):
            msg = "action: accept | result: fail | error: Socket is not a server socket"
            logging.error(msg)
            raise RuntimeError(msg)
        try:
            skt_peer, addr = self.socket.accept()
            return skt_peer, addr
        except OSError as e:
            return None, e
    
    def connect(self):
        if self.ip == "":
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
        if not self.was_closed:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
            self.was_closed = self.socket._closed
            logging.info(f"action: Closed the socket {self.was_closed} 🆓🎊 | result: succes ✅")
    
    def is_closed(self) -> bool:
        return self.was_closed

    def sendall(self, a_object_bytes):
        self.socket.sendall(a_object_bytes)

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
                    return None, 0
            except OSError as e:
                    return self.handler_error_recv_all(bytes_received, f"action: recv_all | result: fail | error: {e}")
            chunks.append(chunk)
            bytes_received += len(chunk)
        return b''.join(chunks), bytes_received
    
    def recv_all_timeout(self, total_bytes_to_receive):
        bytes_received = 0
        chunks = []
        current_timeout = self.socket.gettimeout()
        self.socket.settimeout(2)
        while bytes_received < total_bytes_to_receive:
            try:
                chunk = self.socket.recv(total_bytes_to_receive - bytes_received)
                if chunk == b'':
                    return None, 0
            except OSError as e:
                    return self.handler_error_recv_all(bytes_received, f"action: recv_all | result: fail | error: {e}")
            chunks.append(chunk)
            bytes_received += len(chunk)
        self.socket.settimeout(current_timeout)
        return b''.join(chunks), bytes_received

    def get_peer_name(self):
        return self.socket.getpeername()
        
def aceptarClientes():
    listaPeer = []
    sktAceptador = Socket(port=10108)
    while True:
        sktPeer, addr = sktAceptador.accept_simple()
        print(f"Skt Aceptador  getPeerName: {sktAceptador.socket} addrclient {addr} and port: {sktAceptador.port}")
        print(f"Skt Peer 🔥 My addr: {sktPeer.socket.getsockname()} addr Connect to: {sktPeer.socket.getpeername()}  and port: {sktPeer.port}")
        listaPeer.append(sktPeer)

def client_connect(a_ip):
    sktClient= Socket(ip=a_ip, port=10108)
    result, mssg = sktClient.connect()
    if result:
        print(f"Skt Client ⚡ My addr: {sktClient.socket.getsockname()} addr Connect to: {sktClient.socket.getpeername()}  and port: {sktClient.port}")
    else: 
        print(f"msg: {mssg}")

def server():
    threading.Thread(target=aceptarClientes).start()
    time.sleep(2)
    threading.Thread(target=client_connect, args=("127.0.0.1",)).start()
    threading.Thread(target=client_connect, args=("127.0.0.1",)).start()


def main():
    server()


main()