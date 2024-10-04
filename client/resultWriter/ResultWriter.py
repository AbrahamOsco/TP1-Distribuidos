from common.utils.utils import ResultType
import logging
import json

class ResultWriter:
    def __init__(self):
        self.command_result = {
            ResultType.RESULT_QUERY_1: self.write_query1,
            ResultType.RESULT_QUERY_2: self.write_query2,
            ResultType.RESULT_QUERY_3: self.write_query3,
            ResultType.RESULT_QUERY_4: self.write_query4,
            ResultType.RESULT_QUERY_5: self.write_query5
        }
    
    def run(self, result_query):
        writer_function = self.command_result[result_query["ResultType"]]
        result_query.pop("ResultType")
        writer_function(result_query)

    def write_query1(self, result_query):
        logging.info(f"action: Result Query1: 🕹️ {result_query}| success: ✅")
        with open("/results/query1.json", "w") as json_file:
            json.dump(result_query, json_file, indent=4)
        
    def write_query2(self, result_query):
         logging.info(f"action: Result Query2: 🕹️")

    def write_query3(self, result_query):
        pass
    
    def write_query4(self, result_query):
        pass

    def write_query5(self, result_query):
        pass
