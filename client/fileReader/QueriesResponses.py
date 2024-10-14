import os
from client.fileReader.FileReader import FileReader
import logging
QueriesX = ["Query2", "Query3", "Query4", "Query5"]

class QueriesResponses:
    def __init__(self, should_send_reviews):
        self.responses = {}
        self.percent_of_file_for_use =  float(os.getenv("PERCENT_OF_FILE_FOR_USE"))
        self.loadQuery1()
        if should_send_reviews:
            for query in QueriesX:
                self.loadQueryX(query)
        else:
            self.loadQueryX("Query2")

    def loadQuery1(self):
        reader = FileReader("Query1", percent_of_file_for_use= self.percent_of_file_for_use)
        windows = reader.get_next_line()[0]
        linux = reader.get_next_line()[0]
        mac = reader.get_next_line()[0]
        self.responses["Query1"] = {"windows": windows, "linux": linux, "mac": mac}

    def loadQueryX(self, query):
        reader = FileReader(query, percent_of_file_for_use= self.percent_of_file_for_use)
        self.responses[query] = []
        response = reader.get_next_line()
        while response is not None:
            self.responses[query].append(",".join(response))
            response = reader.get_next_line()

    def diffQuery(self, response1, response2):
        # Find strings only in response1
        only_in_arr1 = [f"+ {item}" for item in response1 if item not in response2]
        # Find strings only in response2
        only_in_arr2 = [f"- {item}" for item in response2 if item not in response1]
        
        # Combine and return
        return only_in_arr1 + only_in_arr2

    def diff(self, responses):
        diff = {}
        for query in self.responses:
            if query not in responses:
                diff[query] = self.responses[query]
            elif query == "Query1":
                diff[query] = []
                for os in self.responses[query]:
                    if int(self.responses[query][os]) != int(responses[query][os]):
                        logging.info(f"OS:{os} Expected: {self.responses[query][os]} | Actual: {responses[query][os]}")
                        diff[query].append(os)
            else:
                diff[query] = self.diffQuery(self.responses[query], responses[query])
        return diff