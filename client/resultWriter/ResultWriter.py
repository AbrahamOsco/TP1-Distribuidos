from common.utils.utils import ResultType
import logging
import json

class ResultWriter:
    def __init__(self):
        self.command_result = {
            ResultType.RESULT_QUERY_1.value: self.write_query,
            ResultType.RESULT_QUERY_2.value: self.write_query,
            ResultType.RESULT_QUERY_3.value: self.write_query,
            ResultType.RESULT_QUERY_4.value: self.write_query,
            ResultType.RESULT_QUERY_5.value: self.write_query
        }
    
    def run(self, result_query):
        number_query = result_query["result_type"]
        writer_function = self.command_result[number_query]
        result_query.pop("result_type")
        writer_function(result_query, number_query)

    def write_query(self, result_query, number_query):
        if (number_query == ResultType.RESULT_QUERY_4.value or number_query == ResultType.RESULT_QUERY_5.value):
            result_query["games"] = list(result_query["games"][0].keys()) # Solo guardamos los names!
        with open(f"/results/query{number_query}.json", "w") as json_file:
            json.dump(result_query, json_file, indent =4)
        result_in_str = json.dumps(result_query, indent =4)
        logging.info(f"action: Query {number_query} file was written | success: ✅")
        logging.info(f"Show results Query {number_query}: {result_in_str}")
