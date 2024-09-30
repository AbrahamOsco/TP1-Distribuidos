from common.utils.utils import initialize_log 
import logging
import os
import time as t 

class Output:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
    
    def run(self):
        logging.info("Output started")