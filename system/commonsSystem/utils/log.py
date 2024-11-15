import logging
import os
def initialize_config_log():
    config_params = {}
    config_params["log_level"] = os.getenv("LOGGING_LEVEL", "INFO")
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
        level=config_params["log_level"],
        datefmt='%Y-%m-%d %H:%M:%S',)
    return config_params

