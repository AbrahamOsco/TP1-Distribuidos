import signal
import time
import threading
import socket
import logging

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
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if (ip == ""):
            self.socket.bind(("", port))
            self.socket.listen(MAX_LISTEN_BACKLOG)
    
    def get_addr(self):
        return self.socket.getsockname()
    
    def get_addr_from_connect(self):
        return self.socket.getpeername()


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
            self.socket.settimeout(2)
            skt_peer, addr = self.socket.accept()
            self.socket.settimeout(None)
            return skt_peer, addr
        except OSError as e:
            return None, e
    
    def connect(self):
        if self.ip == "":
            msg = "action: connect | result: fail | error: Socket is not a client socket"
            logging.error(msg)
            return False, msg
        try:
            self.socket.settimeout(2)
            self.socket.connect((self.ip, self.port))
            self.socket.settimeout(None)
        except (OSError, ConnectionRefusedError) as e:
            return False, e
        return True, ""
    
    def close(self):
        if not self.was_closed:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except OSError as e:
                print("Closing socket with error: " + str(e))
                pass
            self.socket.close()
            self.was_closed = self.socket._closed
    
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
    
    @classmethod
    def get_my_numeric_ip(self,):
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address

def thread_accepter(self, a_socket: Socket):
    while not not a_socket.was_closed():
        try:
            skt_peer, addr = a_socket.accept()
            if skt_peer is not None:
                self.add_socket(skt_peer, addr)
        except OSError as e:
            logging.error(f"action: accept | result: fail | error: {e}")
            break

class Basic:
    
    def __init__(self, port):
        self.skt = Socket("", port)
        self.joins = []
        self.running = threading.Event()
        self.running.set()
        signal.signal(signal.SIGTERM, self.handler_sigterm)
    
    def thr_accepter(self):
        while not self.skt.is_closed():
            try:
                skt_peer, addr = self.skt.accept()
                if skt_peer is not None:
                    self.add_socket(skt_peer, addr)
            except OSError as e:
                logging.error(f"action: accept | result: fail | error: {e}")
                break
    
    def run(self):
        thr = threading.Thread(target=self.thr_accepter, )
        self.joins.append(thr)
        thr.start()
        while self.running.is_set():
            time.sleep(1)

    def handler_sigterm(self, signum, frame):
        print("Signal SIGTERM received ⚡")
        self.skt.close()
        self.running.clear()
        for join in self.joins:
            join.join()
        print("All resource free! ⚡⚡")
        
def main():
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',)
    basic = Basic(5000)
    basic.run()
    

main()

