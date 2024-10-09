from common.utils.utils import ResultType
import logging
import json

class ResultWriter:
    def __init__(self):
        self.command_result = {
            ResultType.RESULT_QUERY_1.value: self.write_query1,
            ResultType.RESULT_QUERY_2.value: self.write_query2,
            ResultType.RESULT_QUERY_3.value: self.write_query3,
            ResultType.RESULT_QUERY_4.value: self.write_query4,
            ResultType.RESULT_QUERY_5.value: self.write_query5
        }
    
    def run(self, result_query):
        writer_function = self.command_result[result_query["result_type"]]
        result_query.pop("result_type")
        writer_function(result_query)

    def write_query1(self, result_query):
        with open("/results/query1.json", "w") as json_file:
            json.dump(result_query, json_file, indent =4)
        result_in_str = json.dumps(result_query, indent =4)
        logging.info(f"action: Query1 file was written | success: ✅")
        logging.info(f"Show results Query 1: {result_in_str}")
        
    def write_query2(self, result_query):
        with open("/results/query2.json", "w") as json_file:
            json.dump(result_query, json_file, indent =4)
        result_in_str = json.dumps(result_query, indent =4)
        logging.info(f"action: Query2 file was written | success: ✅")
        logging.info(f"Show results Query 2: {result_in_str}")

    def write_query3(self, result_query):
        with open("/results/query3.json", "w") as json_file:
            json.dump(result_query, json_file, indent=4)
        result_in_str = json.dumps(result_query, indent =4)
        logging.info(f"action: Query3 file was written | success: ✅")
        logging.info(f"Show results Query 3: {result_in_str}")
    
    def write_query4(self, result_query):
        pass

    def write_query5(self, result_query):
        pass
