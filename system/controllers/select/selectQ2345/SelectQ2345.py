from common.utils.utils import initialize_log 
import logging
import time as t
import os

class SelectQ2345:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))

    def run(self):
       logging.info("SelectQ2345 started")

s