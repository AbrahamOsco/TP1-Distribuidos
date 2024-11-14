import time
import socket

TIME_OUT_HEALTH_CHECK = 1

class HealthCheck: 
    def __init__(self, ip, port, node_id):
        pass
    
    @classmethod
    def is_alive(cls, ip, port, node_id):
        try:
            skt_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            skt_udp.settimeout(self.TIME_OUT_HEALTH_CHECK)
            message = b"ping"
            skt_udp.sendto(message, (self.ip, self.port))
            data, addr = sock.recvfrom(1024)
            if data == b'ping':
                logging.info(f"[{self.node_id}] Ping! ✅ 🌟")
                return True

        except (Exception, socket.timeout) as e:
            logging.info(f"[{self.node_id}] Error in healtcheck {e} 👈")
            return False
