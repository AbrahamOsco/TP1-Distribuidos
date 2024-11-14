import socket
import logging

TIMEOUT_FOR_CHECK_PING = 1

class ServerUDP:
    def __init__(self, node_id: int, port: str):
        self.port = port
        self.node_id = node_id
        self.skt_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.skt_udp.bind(("", port))
        self.skt_udp.settimeout(TIMEOUT_FOR_CHECK_PING)

    def run(self):
        while not self.skt_udp._closed:
            try:
                message, addr = self.skt_udp.recvfrom(1024)
                if message == b"ping":
                    self.skt_udp.sendto(b"ping", addr)
                elif message == b'':
                    logging.info(f"[{self.node_id}] Received empty message, ignoring")
                    continue
                else:
                    logging.info(f"msg recv: {message} ❌")
            except socket.timeout:
                continue
            except Exception as e:
                if not self.skt_udp._closed:
                    logging.info(f"[{self.node_id}] Error in serverUDP 🗡️ ⚡")
                break
    def     stop(self):
        self.skt_udp.close()
