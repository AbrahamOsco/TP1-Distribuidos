import logging
import os
def initialize_config_log():
    config_params = {}
    config_params["log_level"] = os.getenv("LOGGING_LEVEL", "INFO")
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
        level=config_params["log_level"],
        datefmt='%Y-%m-%d %H:%M:%S',)
    return config_params

def get_service_name(id: int):
    return int(f"20{id}")

def get_host_name(id: int):
    return f"node{id-100}"

def ids_to_msg(message: str, ids: list[int]):
    return message + "|" + "|".join([str(x) for x in ids])

    