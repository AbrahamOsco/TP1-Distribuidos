import os
import logging
from client.responses.ResponseReader import ResponseReader

QueriesX = ["Query3", "Query4", "Query5"]

class QueriesResponses:
    def __init__(self, should_send_reviews):
        self.responses = {}
        self.percent_of_file_for_use =  float(os.getenv("PERCENT_OF_FILE_FOR_USE"))
        self.should_send_reviews = should_send_reviews
        self.run()

    def run(self):
        self.load_query1()
        self.load_other_queries("Query2")
        if self.should_send_reviews:
            for query in QueriesX:
                self.load_other_queries(query)

    def load_query1(self):
        reader = ResponseReader(query_name="Query1", percent_of_file_for_use= self.percent_of_file_for_use)
        windows = reader.get_next_line()[0]
        linux = reader.get_next_line()[0]
        mac = reader.get_next_line()[0]
        reader.close()
        self.responses["Query1"] = {"windows": windows, "linux": linux, "mac": mac}

    def load_other_queries(self, query):
        reader = ResponseReader(query_name=query, percent_of_file_for_use= self.percent_of_file_for_use)
        self.responses[query] = []
        response_current = reader.get_next_line()
        while response_current is not None:
            self.responses[query].append(",".join(response_current))
            response_current = reader.get_next_line()

    def diff_query(self, response1, response2):
        # Find strings only in response1
        only_in_arr1 = [f"+ {item}" for item in response1 if item not in response2]
        # Find strings only in response2
        only_in_arr2 = [f"- {item}" for item in response2 if item not in response1]
        
        # Combine and return
        return only_in_arr1 + only_in_arr2

    def diff(self, responses_obtained):
        diff = {}
        for query in self.responses:
            if query not in responses_obtained:
                diff[query] = self.responses[query]
            elif query == "Query1":
                diff[query] = []
                for os in self.responses[query]:
                    if int(self.responses[query][os]) != int(responses_obtained[query][os]):
                        logging.info(f"OS:{os} Expected: {self.responses[query][os]} | Actual: {responses_obtained[query][os]}")
                        diff[query].append(os)
            else:
                diff[query] = self.diff_query(self.responses[query], responses_obtained[query])
        return diff


