import logging
import json


class CompareResults:
    def __init__(self, percent_of_file):
        self.percent_of_file = percent_of_file
    
    def compare(self):
        self.are_equals_in_q1()
        self.are_equals_in_top('2')
        self.are_equals_in_top('3')
        self.are_equals_in_name('4')
        self.are_equals_in_name('5')
    
    def are_equals_in_q1(self):
        result_expect = None
        result_obtained = None
        are_equals = True
        with open("results/query1.json", "r") as file_obtained:
            result_obtained = json.load(file_obtained)
        with open(f"resultsExpect/with{self.percent_of_file}/query1.json", "r") as file_expect:
            result_expect = json.load(file_expect)
        platforms = ["Windows", "Linux", "Mac"]
        for a_platform in platforms:
            if result_obtained[a_platform] != result_expect[a_platform]:
                are_equals = False
        if (are_equals):
            logging.info(f"No hay diferencias en la query1! 💯 ✅")
            

    def are_equals_in_top(self, number_query):
        result_expect = None
        result_obtained = None
        with open(f"results/query{number_query}.json", "r") as file_obtained:
            result_obtained = json.load(file_obtained)
        with open(f"resultsExpect/with{self.percent_of_file}/query{number_query}.json", "r") as file_expect:
            result_expect = json.load(file_expect)

        games_expect = result_expect["games"][0]
        games_obtained = result_obtained["games"][0]
        
        same_game_names = set(games_expect.keys()) == set(games_obtained.keys())

        same_values = all( games_expect[game_name] == games_obtained[game_name]  for game_name in games_expect)

        for game_name in games_expect:
            if games_expect[game_name] != games_obtained[game_name]:
                logging.info(f"En la Query {number_query}: El juego '{game_name}' tiene valores diferentes:\
                            Expect {games_expect[game_name]} Obtiene: {games2.games_obtained[game_name]}")
        if same_game_names and same_values:
            logging.info(f"No hay diferencias en la query{number_query}! 💯 ✅")

    def are_equals_in_name(self, number_query):
        result_expect = None
        result_obtained = None
        with open(f"results/query{number_query}.json", "r") as file_obtained:
            result_obtained = json.load(file_obtained)
        with open(f"resultsExpect/with{self.percent_of_file}/query{number_query}.json", "r") as file_expect:
            result_expect = json.load(file_expect)

        games_expect = result_expect["games"]
        games_obtained = result_obtained["games"]
        if set(games_expect) == set(games_obtained):
            logging.info(f"No hay diferencias en la query{number_query}! 💯 ✅")
        else:
            logging.info(f"Hay diferencias en la query{number_query}! 💯 ✅")
             # Ver juegos que faltan en uno u otro archivo
            logging.info(f"(games_expect: {games_expect} games_obtained: {games_obtained}")
            missing_in_obtained = set(games_expect) - set(games_obtained)
            missing_in_expect = set(games_obtained) - set(games_expect)
            if missing_in_obtained:
                logging.info(f"Juegos en 'expect' que faltan en 'obtained': {missing_in_obtained}")
            elif missing_in_expect:
                logging.info(f"Juegos en 'obtained' que faltan en 'expect': {missing_in_expect}")


