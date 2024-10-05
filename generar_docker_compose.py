import sys

images = {
    "platformreducer": "platformcounter",
    "selectidnameindie": "selectidname",
    "selectidnameaction": "selectidname",
    "filterscorepositive": "filterscore",
    "filterscorenegative": "filterscore",
}

sources = {
    "selectq1": "DataParsed",
    "selectq2345": "DataParsed",
    "platformcounter": "GamesPlatform",
    "platformreducer": "CountByPlatform",
    "filtergender": "GamesQ2345",
    "filterdecade": "GenderGames",
    "groupertopaverageplaytime": "DecadeGames",
    "selectidnameindie": "GenderGames",
    "selectidnameaction": "GenderGames",
    "filterscorepositive": "DataParsed",
    "filterscorenegative": "DataParsed",
    "monitorstorageq3": "ReviewsPositives,MonitorQ3",
    "groupertopreviewspositiveindie": "IndieGamesReviewed",
    "monitorjoinerq4": "ReviewsNegatives,MonitorQ45",
    "filterreviewenglish": "ActionGamesReviewed",
    "monitorstorageq4": "ActionGamesEnglishReviews",
    "monitorstorageq5": "ReviewsNegatives,MonitorQ45",
}

source_keys = {
    "selectq1": "games",
    "selectq2345": "games",
    "filterdecade": "Indie",
    "selectidnameindie": "Indie",
    "selectidnameaction": "Action",
    "filterscorepositive": "reviews",
    "filterscorenegative": "reviews",
    "monitorstorageq3": "default,default",
    "monitorjoinerq4": "default,default",
    "monitorstorageq5": "default,default",
}

source_types = {
    "selectq1": "topic",
    "selectq2345": "topic",
    "filterdecade": "topic",
    "selectidnameindie": "topic",
    "selectidnameaction": "topic",
    "filterscorepositive": "topic",
    "filterscorenegative": "topic",
    "monitorstorageq3": "direct,direct",
    "monitorjoinerq4": "fanout,fanout",
    "monitorstorageq5": "fanout,fanout",
}

sinks = {
    "selectq1": "GamesPlatform",
    "selectq2345": "GamesQ2345",
    "platformcounter": "CountByPlatform",
    "platformreducer": "Output",
    "filtergender": "GenderGames",
    "filterdecade": "DecadeGames",
    "groupertopaverageplaytime": "Output",
    "selectidnameindie": "MonitorQ3",
    "selectidnameaction": "MonitorQ45",
    "filterscorepositive": "ReviewsPositives",
    "filterscorenegative": "ReviewsNegatives",
    "monitorstorageq3": "IndieGamesReviewed",
    "groupertopreviewspositiveindie": "Output",
    "monitorjoinerq4": "ActionGamesReviewed",
    "filterreviewenglish": "ActionGamesEnglishReviews",
    "monitorstorageq4": "Output",
    "monitorstorageq5": "Output",
}

sink_types = {
    "filtergender": "topic",
    "selectidnameaction": "fanout",
    "filterscorenegative": "fanout",
}

service_should_be_included = {
    "selectq1": lambda queries: 1 in queries,
    "selectq2345": lambda queries: 2 in queries or 3 in queries or 4 in queries or 5 in queries,
    "platformcounter": lambda queries: 1 in queries,
    "platformreducer": lambda queries: 1 in queries,
    "filtergender": lambda queries: 2 in queries or 3 in queries or 4 in queries or 5 in queries,
    "filterdecade": lambda queries: 2 in queries,
    "groupertopaverageplaytime": lambda queries: 2 in queries,
    "selectidnameindie": lambda queries: 3 in queries,
    "selectidnameaction": lambda queries: 4 in queries or 5 in queries,
    "filterscorepositive": lambda queries: 3 in queries,
    "filterscorenegative": lambda queries: 4 in queries or 5 in queries,
    "monitorstorageq3": lambda queries: 3 in queries,
    "groupertopreviewspositiveindie": lambda queries: 3 in queries,
    "monitorjoinerq4": lambda queries: 4 in queries,
    "filterreviewenglish": lambda queries: 4 in queries,
    "monitorstorageq4": lambda queries: 4 in queries,
    "monitorstorageq5": lambda queries: 5 in queries,
}

entrypoints = {
    "selectq1": "/app/system/controllers/select/selectQ1/main.py",
    "selectq2345": "/app/system/controllers/select/selectQ2345/main.py",
    "platformcounter": "/app/system/controllers/groupers/platformCounter/main.py",
    "platformreducer": "/app/system/controllers/groupers/platformCounter/main.py",
    "filtergender": "/app/system/controllers/filters/filterGender/main.py",
    "filterdecade": "/app/system/controllers/filters/filterDecade/main.py",
    "groupertopaverageplaytime": "/app/system/controllers/groupers/grouperTopAveragePlaytime/main.py",
    "selectidnameindie": "/app/system/controllers/select/selectIDName/main.py",
    "selectidnameaction": "/app/system/controllers/select/selectIDName/main.py",
    "filterscorepositive": "/app/system/controllers/filters/filterScore/main.py",
    "filterscorenegative": "/app/system/controllers/filters/filterScore/main.py",
    "monitorstorageq3": "/app/system/controllers/storages/monitorStorageQ3/main.py",
    "groupertopreviewspositiveindie": "/app/system/controllers/groupers/grouperTopReviewsPositiveIndie/main.py",
    "monitorjoinerq4": "/app/system/controllers/joiners/monitorJoinerQ4/main.py",
    "filterreviewenglish": "/app/system/controllers/filters/filterReviewEnglish/main.py",
    "monitorstorageq4": "/app/system/controllers/storages/monitorStorageQ4/main.py",
    "monitorstorageq5": "/app/system/controllers/storages/monitorStorageQ5/main.py",
}

node_amounts = {}

depends = {
    "selectq1": ["platformcounter"],
    "selectq2345": ["filtergender"],
    "platformcounter": ["platformreducer"],
    "filtergender": ["selectidnameaction", "selectidnameindie", "filterdecade"],
    "filterdecade": ["groupertopaverageplaytime"],
    "selectidnameindie": ["monitorstorageq3"],
    "selectidnameaction": ["monitorjoinerq4", "monitorstorageq5"],
    "filterscorepositive": ["monitorstorageq3"],
    "filterscorenegative": ["monitorjoinerq4", "monitorstorageq5"],
    "monitorstorageq3": ["groupertopreviewspositiveindie"],
    "monitorjoinerq4": ["filterreviewenglish"],
    "filterreviewenglish": ["monitorstorageq4"],
}

def special_envs(service_name):
    if service_name == "filtergender":
        return """
        - GENDERS=Indie,Action"""
    if service_name == "filterdecade":
        return """
        - DECADE=2010"""
    if service_name == "groupertopaverageplaytime":
        return """
        - TOP_SIZE=10"""
    if service_name == "groupertopreviewspositiveindie":
        return """
        - TOP_SIZE=5"""
    if service_name == "monitorstorageq4":
        return """
        - AMOUNT_NEEDED=5000"""
    if service_name == "monitorstorageq5":
        return """
        - PERCENTILE=0.9"""
    if service_name == "filterscorepositive":
        return """
        - SCORE_WANTED=1"""
    if service_name == "filterscorenegative":
        return """
        - SCORE_WANTED=-1"""
    return ""

def get_depends_and_envs(queries, service_name:str, i:int=0):
    base = f"""
    depends_on:
        rabbitmq:
            condition: service_healthy"""
    service_depends = depends.get(service_name, [])
    for depend in service_depends:
        if not service_should_be_included[depend](queries):
            continue
        if depend not in node_amounts:
            base += f"""
        {depend}:
            condition: service_started"""
        else:
            for j in range(node_amounts[depend]):
                base += f"""
        {depend}_{j}:
            condition: service_started"""
    base += f"""
    environment:
        - LOGGING_LEVEL=INFO
        - PYTHONPATH=/app
        - NODE_NAME={service_name}
        - NODE_ID={i}
        - SOURCE={sources[service_name]}
        - SOURCE_KEY={source_keys.get(service_name, "default")}
        - SOURCE_TYPE={source_types.get(service_name, "direct")}
        - SINK={sinks[service_name]}
        - SINK_TYPE={sink_types.get(service_name, "direct")}"""
    base += special_envs(service_name)
    return base

def generar_servicio_escalable(queries, service_name):
    if not service_should_be_included[service_name](queries):
        return ""
    amount = node_amounts[service_name]
    base = ""
    for i in range(amount):
        base += f"""

  {service_name}_{i}:
    container_name: {service_name}_{i}
    image: {images.get(service_name, service_name)}:latest
    entrypoint: python3 {entrypoints[service_name]}
    networks:
        - system_network
    restart: on-failure{get_depends_and_envs(queries, service_name, i)}"""
    return base
        
def generar_servicio_no_escalable(queries, service_name):
    if not service_should_be_included[service_name](queries):
        return ""
    base = f"""

  {service_name}:
    container_name: {service_name}
    image: {images.get(service_name, service_name)}:latest
    entrypoint: python3 {entrypoints[service_name]}
    networks:
        - system_network
    restart: on-failure{get_depends_and_envs(queries, service_name)}"""
    return base


def get_gateway(queries, select_q1:int=0, select_q2345:int=0, filter_score_positive:int=0, filter_score_negative:int=0):
    base = """

  gateway:
    container_name: gateway
    image: gateway:latest
    entrypoint: python3 /app/system/controllers/gateway/main.py
    networks:
        - system_network
    restart: on-failure
    environment:
        - LOGGING_LEVEL=INFO
        - PYTHONPATH=/app
        - NODE_NAME=gateway
        - NODE_ID=1
        - SOURCE=Output
        - SINK=DataParsed
        - SINK_TYPE=topic
    depends_on:
      rabbitmq:
        condition: service_healthy"""
    if 1 in queries:
        for i in range(select_q1):
            base += f"""
      selectQ1_{i}:
        condition: service_started"""
    if 2 in queries or 3 in queries or 4 in queries or 5 in queries:
        for i in range(select_q2345):
            base += f"""
      selectQ2345{i}:
        condition: service_started"""
    if 3 in queries:
        for i in range(filter_score_positive):
            base += f"""
      filterscorepositive_{i}:
        condition: service_started"""
    if 4 in queries or 5 in queries:
        for i in range(filter_score_negative):
            base += f"""
      filterscorenegative_{i}:
        condition: service_started"""
    return base

def generar_docker_compose(output_file:str, queries=[], select_q1="0", platform_counter="0", select_q2345="0", filter_gender="0",
                           filter_decade="0", select_id_name_indie="0", select_id_name_action="0", filter_score_positive="0",
                           filter_review_english="0", filter_score_negative="0"):
    node_amounts["selectq1"] = int(select_q1)
    node_amounts["platformcounter"] = int(platform_counter)
    node_amounts["selectq2345"] = int(select_q2345)
    node_amounts["filtergender"] = int(filter_gender)
    node_amounts["filterdecade"] = int(filter_decade)
    node_amounts["selectidnameindie"] = int(select_id_name_indie)
    node_amounts["selectidnameaction"] = int(select_id_name_action)
    node_amounts["filterscorepositive"] = int(filter_score_positive)
    node_amounts["filterreviewenglish"] = int(filter_review_english)
    node_amounts["filterscorenegative"] = int(filter_score_negative)
    compose = """
services:
  rabbitmq:
    container_name: rabbitmq
    image: rabbit:latest
    ports:
      - "5672:5672"
      - "15672:15672"
    networks:
      - system_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:15672"]
      interval: 10s
      timeout: 5s
      retries: 10
      start_period: 15s

  client1:
    container_name: client1
    image: client:latest
    entrypoint: python3 /app/client/main.py
    volumes:
      - ./data/games.csv:/data/games.csv
      - ./data/dataset.csv:/data/dataset.csv
    environment:
      - NODE_ID=1
      - LOGGING_LEVEL=INFO
      - PYTHONPATH=/app
      - HOSTNAME=gateway
    networks:
      - system_network
    restart: on-failure
    depends_on:
      rabbitmq:
        condition: service_healthy
      gateway:
        condition: service_started"""

    compose += get_gateway(queries)

    compose += generar_servicio_escalable(queries, "selectq1")
    compose += generar_servicio_escalable(queries, "platformcounter")
    compose += generar_servicio_no_escalable(queries, "platformreducer")
    compose += generar_servicio_escalable(queries, "selectq2345")
    compose += generar_servicio_escalable(queries, "filtergender")
    compose += generar_servicio_escalable(queries, "filterdecade")
    compose += generar_servicio_no_escalable(queries, "groupertopaverageplaytime")
    compose += generar_servicio_escalable(queries, "selectidnameindie")
    compose += generar_servicio_escalable(queries, "filterscorepositive")
    compose += generar_servicio_no_escalable(queries, "monitorstorageq3")
    compose += generar_servicio_no_escalable(queries, "groupertopreviewspositiveindie")
    compose += generar_servicio_escalable(queries, "selectidnameaction")
    compose += generar_servicio_escalable(queries, "filterscorenegative")
    compose += generar_servicio_no_escalable(queries, "monitorjoinerq4")
    compose += generar_servicio_escalable(queries, "filterreviewenglish")
    compose += generar_servicio_no_escalable(queries, "monitorstorageq4")
    compose += generar_servicio_no_escalable(queries, "monitorstorageq5")
    compose += """

networks:
  system_network:
    ipam:
      driver: default
      config:
        - subnet: 172.25.125.0/24
"""

    with open(output_file, 'w') as f:
        f.write(compose)

    print(f"{output_file} generado con los siguientes parámetros:")
    print(f"SelectQ1: {select_q1}, PlatformCounter: {platform_counter}, "
          f"SelectQ2345: {select_q2345}, FilterGender: {filter_gender}, FilterDecade: {filter_decade}, "
          f"SelectIDNameIndie: {select_id_name_indie}, SelectIDNameAction: {select_id_name_action}, "
          f"FilterScorePositive: {filter_score_positive}, FilterReviewEnglish: {filter_review_english}, "
          f"FilterScoreNegative: {filter_score_negative}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Se debe ingresar: python generar_docker_compose.py <nombre_archivo_salida> <Queries>")
        sys.exit(1)
    query_input = sys.argv[2]
    if query_input == "A":
        queries = [1, 2, 3, 4, 5]
    elif query_input in ["1", "2", "3", "4", "5"]:
        queries = [int(query_input)]
    else:
        print("Invalid Query")
        sys.exit(1)
    if query_input == "A":
        if len(sys.argv) != 13:
            print("Se debe ingresar: python generar_docker_compose.py <nombre_archivo_salida> <Queries> [SelectQ1] [PlatformCounter] [SelectQ2345] [FilterGender] [FilterDecade] [SelectIDNameIndie] [FilterScorePositive] [SelectIDNameAction] [FilterScoreNegative] [FilterReviewEnglish]")
            sys.exit(1)
        generar_docker_compose(output_file=sys.argv[1], queries=queries, select_q1=sys.argv[3], platform_counter=sys.argv[4],
                               select_q2345=sys.argv[5], filter_gender=sys.argv[6], filter_decade=sys.argv[7],
                                 select_id_name_indie=sys.argv[8], filter_score_positive=sys.argv[9],
                                    select_id_name_action=sys.argv[10], filter_score_negative=sys.argv[11],
                                    filter_review_english=sys.argv[12])
    elif query_input == "1":
        if len(sys.argv) != 5:
            print("Se debe ingresar: python generar_docker_compose.py <nombre_archivo_salida> <Queries> [SelectQ1] [PlatformCounter]")
            sys.exit(1)
        generar_docker_compose(output_file=sys.argv[1], queries=queries, select_q1=sys.argv[3], platform_counter=sys.argv[4])
    elif query_input == "2":
        if len(sys.argv) != 6:
            print("Se debe ingresar: python generar_docker_compose.py <nombre_archivo_salida> <Queries> [SelectQ2345] [FilterGender] [FilterDecade]")
            sys.exit(1)
        generar_docker_compose(output_file=sys.argv[1], queries=queries, select_q2345=sys.argv[3], filter_gender=sys.argv[4],
                               filter_decade=sys.argv[5])
    elif query_input == "3":
        if len(sys.argv) != 7:
            print("Se debe ingresar: python generar_docker_compose.py <nombre_archivo_salida> <Queries> [SelectQ2345] [FilterGender] [SelectIDNameIndie] [FilterScorePositive] ")
            sys.exit(1)
        generar_docker_compose(output_file=sys.argv[1], queries=queries, select_q2345=sys.argv[3], filter_gender=sys.argv[4],
                               select_id_name_indie=sys.argv[5], filter_score_positive=sys.argv[6])
    elif query_input == "4":
        if len(sys.argv) != 8:
            print("Se debe ingresar: python generar_docker_compose.py <nombre_archivo_salida> <Queries> [SelectQ2345] [FilterGender] [SelectIDNameAction] [FilterScoreNegative] [FilterReviewEnglish]")
            sys.exit(1)
        generar_docker_compose(output_file=sys.argv[1], queries=queries, select_q2345=sys.argv[3], filter_gender=sys.argv[4],
                               select_id_name_action=sys.argv[5], filter_score_negative=sys.argv[6], filter_review_english=sys.argv[7])
    elif query_input == "5":
        if len(sys.argv) != 7:
            print("Se debe ingresar: python generar_docker_compose.py <nombre_archivo_salida> <Queries> [SelectQ2345] [FilterGender] [SelectIDNameAction] [FilterScoreNegative]")
            sys.exit(1)
        generar_docker_compose(output_file=sys.argv[1], queries=queries, select_q2345=sys.argv[3], filter_gender=sys.argv[4],
                               select_id_name_action=sys.argv[5], filter_score_negative=sys.argv[6])
    else:
        print("Invalid Query")
        sys.exit(1)