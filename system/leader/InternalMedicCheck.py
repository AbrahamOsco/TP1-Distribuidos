from system.commonsSystem.utils.connectionLeader import get_host_name, get_service_name
from system.leader.common_leader import OFFSET_MEDIC_SERVER_INTERN
import logging
import traceback
import time
import socket
import logging
import threading

TIME_OUT_HEALTH_CHECK = 5 #ensegundos
FAIL = 0
SUCCESS = 1

class InternalMedicCheck:
    hostname = None
    service_name = None
    socket = None
    offset_time_conecction_ready = 2 #Si ya se armo el anillo entonces, reducimos el timeout a 3. (5-2 = 3)

    @classmethod
    def sender(cls):
        message = "ping".encode('utf-8')
        while True:
            try:
                logging.info(f"Send ping to {(cls.hostname, cls.service_name)} 🔥🔥🅰️")
                cls.socket.sendto(message, (cls.hostname, cls.service_name))
            except OSError as e:
                return

    @classmethod
    def is_alive(cls, my_id, node_id_to_check) -> bool:
        cls.hostname = get_host_name(node_id_to_check)
        cls.service_name = get_service_name(node_id_to_check + OFFSET_MEDIC_SERVER_INTERN)
        cls.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cls.socket.settimeout(TIME_OUT_HEALTH_CHECK - cls.offset_time_conecction_ready)
        try:
            thr_sender = threading.Thread(target= cls.sender)
            thr_sender.start()
            data, addr = cls.socket.recvfrom(1024)
            logging.info(f"Response of ping of {(cls.hostname, cls.service_name)}  ⚡⚡🅱️")
            if data == b'ping':
                logging.info(f"[{my_id}] Now it's Connected with {node_id_to_check} OK!. ✅")
                cls.socket.close()
                thr_sender.join()
                return True
        except socket.timeout:
            logging.info(f"[{my_id}] This Node [{node_id_to_check}] is 💀 Timeout!")
            cls.socket.close()
            thr_sender.join()
            return False
        except socket.gaierror as e:
            logging.error(f"[{my_id}] -> Node: [{node_id_to_check}] is falling Error: {e}  👈")
            cls.socket.close()
            thr_sender.join()
            return False
        except Exception as e:
            cls.socket.close()
            thr_sender.join()
            traceback.print_exc()
            logging.info(f"[{node_id_to_check}] Other type of Error in healtcheck {e} 👈")
            return False
        return False