import logging
import traceback
import time
import socket
import logging
import threading

TIME_OUT_HEALTH_CHECK = 1  # en segundos

FAIL = 0
SUCCESS = 1

class InternalHealthCheck: 
    def __init__(self, ip, port, node_id):
        pass

    @classmethod
    def is_alive(cls, ip, port, my_id, node_id_to_check) -> bool:
        try:
            skt_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #skt_udp.connect((ip, port))
            message = b"ping"
            skt_udp.sendto(message, (ip, port))
            skt_udp.settimeout(TIME_OUT_HEALTH_CHECK)
            data, addr = skt_udp.recvfrom(1024)
            if data == b'ping':
                logging.info(f"[{my_id}] HealthCheck to {node_id_to_check} OK!. ✅")
                return True
            else:
                return False
        except socket.timeout:
            logging.info(f"[{my_id}] -> Node: [{node_id_to_check}] Timeout!")
            return False
        except socket.gaierror as e:
            logging.error(f"[{my_id}] -> Node: [{node_id_to_check}] is falling Error: {e}  👈")
            return False
        except Exception as e:
            # Imprime la traza completa del error
            traceback.print_exc()
            logging.info(f"[{node_id_to_check}] Other type of Error in healtcheck {e} 👈")
            return False
        finally:
            skt_udp.close()
        return False