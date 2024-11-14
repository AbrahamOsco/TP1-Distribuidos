import socket
import logging

class ServerUDP:
    def __init__(self, node_id: int, port: str):
        self.port = port
        self.node_id = node_id
        self.skt_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.skt_udp.bind(("", port))

    def run(self):
        while True:
            try: 
                message, addr = self.skt_udp.recvfrom(1024)
                if message == b"ping":
                    self.skt_udp.sendto(b"ping", addr)
                    logging.info(f"[{self.node_id}] message is : {message}")
                else: 
                     logging.info(f"msg recv: {message} ❌")
                     raise Exception("Error in SOCKET UDP ❌ 🎪")
            except Exception as e:
                if not self.skt_udp._closed:
                    logging.info(f"[{self.node_id}] Error in serverUDP 🗡️ ⚡")

    def stop(self):
        self.skt_udp.close()
        logging.info(f"[{self.node_id}] action: Closed the socket 🆓🎊 | result: succes ✅")
