from common.utils.utils import initialize_log 
import logging
import time as t
import os

class SelectQ345:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))

    def run(self):
       logging.info("SelectQ345 started")

