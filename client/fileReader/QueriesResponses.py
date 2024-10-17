import os
from client.fileReader.FileReader import FileReader
import logging

class QueriesResponses:
    def __init__(self, percent_of_file_for_use=1, queries_executed="1"):
        self.responses = {}
        self.percent_of_file_for_use = percent_of_file_for_use
        self.queries_executed = self.parse_queries_executed(queries_executed)
        self.loadQueries()

    def parse_queries_executed(self, queries_executed):
        if isinstance(queries_executed, str):
            return [int(q.strip()) for q in queries_executed.strip('[]').split(',')]
        elif isinstance(queries_executed, int):
            return [queries_executed]
        elif isinstance(queries_executed, list):
            return queries_executed
        else:
            raise ValueError(f"Unsupported type for queries_executed: {type(queries_executed)}")

    def loadQueries(self):
        for query in self.queries_executed:
            if query == 1:
                self.loadQuery1()
            else:
                self.loadQueryX(f"Query{query}")

    def loadQuery1(self):
        reader = FileReader("Query1", percent_of_file_for_use=self.percent_of_file_for_use)
        windows = reader.get_next_line()[0]
        linux = reader.get_next_line()[0]
        mac = reader.get_next_line()[0]
        self.responses["Query1"] = {"windows": windows, "linux": linux, "mac": mac}

    def loadQueryX(self, query):
        reader = FileReader(query, percent_of_file_for_use=self.percent_of_file_for_use)
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