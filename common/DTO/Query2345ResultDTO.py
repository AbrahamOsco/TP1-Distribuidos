OPERATION_TYPE_QUERY2345 = 2

import logging
class Query2345ResultDTO:
    def __init__(self, query=0, games=[]):
        self.operation_type = OPERATION_TYPE_QUERY2345
        self.query = query
        self.games = games
    
    def print(self):
        logging.info(f"Result query {self.query}")
        for game in self.games:
            logging.info(game)
        logging.info("")