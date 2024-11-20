import sys
import random

images = {
    "platformreducer": "platformcounter",
    "selectidnameindie": "selectidname",
    "selectidnameaction": "selectidname",
    "filterscorepositive": "filterscore",
    "filterscorenegative": "filterscore",
    "selectq1": "select",
    "selectidnameindie": "select",
    "selectidnameaction": "select",
    "selectq2345": "select",
}

sources = {
    "filterbasic": "DataRaw",
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
    "filterbasic": "DataParsed",
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
    "filterbasic": "topic",
    "filtergender": "topic",
    "selectidnameaction": "fanout",
    "filterscorenegative": "fanout",
}

service_should_be_included = {
    "filterbasic": lambda _: True,
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
    "filterbasic": "/app/system/controllers/filters/filterBasic/main.py",
    "selectq1": "/app/system/controllers/select/main.py",
    "selectq2345": "/app/system/controllers/select/main.py",
    "platformcounter": "/app/system/controllers/groupers/platformCounter/main.py",
    "platformreducer": "/app/system/controllers/groupers/platformCounter/main.py",
    "filtergender": "/app/system/controllers/filters/filterGender/main.py",
    "filterdecade": "/app/system/controllers/filters/filterDecade/main.py",
    "groupertopaverageplaytime": "/app/system/controllers/groupers/grouperTopAveragePlaytime/main.py",
    "selectidnameindie": "/app/system/controllers/select/main.py",
    "selectidnameaction": "/app/system/controllers/select/main.py",
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
    "filterbasic": ["selectq1", "selectq2345", "filterscorepositive", "filterscorenegative"],
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

def special_envs(service_name, id):
    if service_name == "filtergender":
        return """
        - GENDERS=Indie,Action"""
    if service_name == "filterdecade":
        return """
        - DECADE=2010"""
    if service_name == "groupertopaverageplaytime":
        return """
        - TOP_SIZE=10
        - QUERY=2"""
    if service_name == "groupertopreviewspositiveindie":
        return """
        - TOP_SIZE=5
        - QUERY=3"""
    if service_name == "monitorstorageq4":
        return """
        - AMOUNT_NEEDED=5000
        - QUERY=4"""
    if service_name == "monitorstorageq5":
        return """
        - PERCENTILE=0.9
        - QUERY=5"""
    if service_name == "filterscorepositive":
        return """
        - SCORE_WANTED=1"""
    if service_name == "filterscorenegative":
        return """
        - SCORE_WANTED=-1"""
    if service_name == "selectidnameindie" or service_name == "selectidnameaction":
        return """
        - SELECT=6"""
    if service_name == "selectq1":
        return f"""
        - SELECT=2
        - SEND_MODULO={node_amounts.get("platformcounter", 1)}"""
    if service_name == "selectq2345":
        return """
        - SELECT=3"""
    if service_name == "platformcounter":
        return f"""
        - SOURCE_NAME=platformcounter{id}"""
    if service_name == "platformreducer":
        return f"""
        - QUERY=1"""
    return ""

def get_source_key(service_name, i):
    if service_name == "platformcounter":
        return f"{i}"
    return source_keys.get(service_name, "default")

def get_depends_and_envs(queries, service_name:str, i:int=0, service_instance_name:str=None):
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
        - NODE_NAME={service_instance_name or service_name}
        - NODE_ID={i}
        - AMOUNT_OF_NODES={node_amounts.get(service_name, 1)}
        - SOURCE={sources[service_name]}
        - SOURCE_KEY={get_source_key(service_name, i)}
        - SOURCE_TYPE={source_types.get(service_name, "direct")}
        - SINK={sinks[service_name]}
        - SINK_TYPE={sink_types.get(service_name, "direct")}"""
    base += special_envs(service_name, i)
    return base

def add_persistence_to_pc(service_name):
    if service_name != "platformcounter":
        return ""
    return f"""
    volumes:
      - ./persistent:/persistent"""

def generar_servicio_escalable(queries, service_name, node_id):
    if not service_should_be_included[service_name](queries):
        return ""
    amount = node_amounts[service_name]
    base = ""
    for i in range(amount):
        node_id[0] += 1
        service_instance_name = f"{service_name}_{i}"
        base += f"""
        
  {service_instance_name}:
    container_name: {service_instance_name}
    image: {images.get(service_name, service_name)}:latest
    entrypoint: python3 {entrypoints[service_name]}
    networks:
        - system_network{add_persistence_to_pc(service_name)}
    restart: on-failure{get_depends_and_envs(queries, service_name, node_id[0], service_instance_name)}"""
    return base
        
def generar_servicio_no_escalable(queries, service_name, node_id):
    if not service_should_be_included[service_name](queries):
        return ""
    node_id[0] += 1
    base = f"""
    
  {service_name}:
    container_name: {service_name}
    image: {images.get(service_name, service_name)}:latest
    entrypoint: python3 {entrypoints[service_name]}
    networks:
        - system_network
    volumes:
      - ./persistent:/persistent
    restart: on-failure{get_depends_and_envs(queries, service_name, node_id[0])}"""
    return base


def get_gateway(queries, node_id):
    node_id[0] += 1
    base = f"""
    
  gateway:
    container_name: gateway
    image: gateway:latest
    entrypoint: python3 /app/system/controllers/gateway/main.py
    networks:
        - system_network
    restart: on-failure
    volumes:
      - ./persistent:/persistent
    environment:
        - LOGGING_LEVEL=INFO
        - PYTHONPATH=/app
        - NODE_NAME=gateway
        - NODE_ID={node_id[0]}
        - SOURCE=Output
        - SINK=DataRaw
        - AMOUNT_OF_QUERIES={len(queries)}
    depends_on:
      rabbitmq:
        condition: service_healthy"""
    for i in range(node_amounts["filterbasic"]):
        base += f"""
      filterbasic_{i}:
        condition: service_started"""
    return base

def get_medicos():
    compose = ""
    num_medics = 4
    for i in range(0, num_medics):
        depends_on = (
            f"""
    depends_on:
      medic_{i - 1}:
        condition: service_started"""
            if i > 0
            else ""
        )
        compose += f"""
  medic_{i}:
    container_name: medic_{i}
    image: leader:latest
    entrypoint: python3 -u /app/system/leader/main.py
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - NODE_NAME=medic_{i}  
      - NODE_ID={500+i}
      - LOGGING_LEVEL=INFO
      - RING_SIZE=4
      - PYTHONPATH=/app
    networks:
      - system_network{depends_on}
    """
    return compose


def add_clients(amount, porcentaje_por_ejecucion_para_cliente, queries, node_id):
    compose = ""
    ejecuciones = porcentaje_por_ejecucion_para_cliente.split(';')
    for i in range(1, int(amount)+1):
        node_id[0] += 1
        ejecucion = ejecuciones[i-1]
        compose += f"""

  client{i}:
    container_name: client{i}
    image: client:latest
    entrypoint: python3 /app/client/main.py
    volumes:
      - ./data/games.csv:/data/games.csv
      - ./data/dataset.csv:/data/dataset.csv
      - ./data/responses:/data/responses
      - ./persistent:/persistent
    environment:
      - QUERIES_EXECUTED={queries}  
      - PERCENT_OF_FILE_FOR_USE_BY_EXECUTION={ejecucion}
      - LOGGING_LEVEL=INFO
      - PYTHONPATH=/app
      - HOSTNAME=gateway
      - NODE_NAME=client{i}
      - NODE_ID={node_id[0]}
      - SEND_REVIEWS={1 if (3 in queries or 4 in queries or 5 in queries) else 0}
    networks:
      - system_network
    restart: on-failure
    depends_on:
      rabbitmq:
        condition: service_healthy
      gateway:
        condition: service_started"""
    return compose

def generar_docker_compose(output_file:str, queries=[], filterbasic="0", select_q1="0", platform_counter="0", select_q2345="0", filter_gender="0",
                           filter_decade="0", select_id_name_indie="0", select_id_name_action="0", filter_score_positive="0",
                           filter_review_english="0", filter_score_negative="0", clients="1", porcentaje_por_ejecucion_para_cliente=""):
    node_amounts["filterbasic"] = int(filterbasic)
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
    compose = f"""
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
    
"""

    compose += get_medicos()
    node_id = [99]
    compose += add_clients(int(clients), porcentaje_por_ejecucion_para_cliente, queries, node_id)
    compose += get_gateway(queries, node_id)

    compose += generar_servicio_escalable(queries, "filterbasic", node_id)
    compose += generar_servicio_escalable(queries, "selectq1", node_id)
    compose += generar_servicio_escalable(queries, "platformcounter", node_id)
    compose += generar_servicio_no_escalable(queries, "platformreducer", node_id)
    compose += generar_servicio_escalable(queries, "selectq2345", node_id)
    compose += generar_servicio_escalable(queries, "filtergender", node_id)
    compose += generar_servicio_escalable(queries, "filterdecade", node_id)
    compose += generar_servicio_no_escalable(queries, "groupertopaverageplaytime", node_id)
    compose += generar_servicio_escalable(queries, "selectidnameindie", node_id)
    compose += generar_servicio_escalable(queries, "filterscorepositive", node_id)
    compose += generar_servicio_no_escalable(queries, "monitorstorageq3", node_id)
    compose += generar_servicio_no_escalable(queries, "groupertopreviewspositiveindie", node_id)
    compose += generar_servicio_escalable(queries, "selectidnameaction", node_id)
    compose += generar_servicio_escalable(queries, "filterscorenegative", node_id)
    compose += generar_servicio_no_escalable(queries, "monitorjoinerq4", node_id)
    compose += generar_servicio_escalable(queries, "filterreviewenglish", node_id)
    compose += generar_servicio_no_escalable(queries, "monitorstorageq4", node_id)
    compose += generar_servicio_no_escalable(queries, "monitorstorageq5", node_id)
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
    print(f"FilterBasic: {filterbasic}, SelectQ1: {select_q1}, PlatformCounter: {platform_counter}, "
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
        if len(sys.argv) != 16:
            print("Se debe ingresar: python generar_docker_compose.py <nombre_archivo_salida> <Queries> [FilterBasic] [SelectQ1] [PlatformCounter] [SelectQ2345] [FilterGender] [FilterDecade] [SelectIDNameIndie] [FilterScorePositive] [SelectIDNameAction] [FilterScoreNegative] [FilterReviewEnglish] [NumClients] [EjecucionesPorCliente]")
            sys.exit(1)
        generar_docker_compose(output_file=sys.argv[1], queries=queries, filterbasic=sys.argv[3], select_q1=sys.argv[4], platform_counter=sys.argv[5],
                               select_q2345=sys.argv[6], filter_gender=sys.argv[7], filter_decade=sys.argv[8],
                                 select_id_name_indie=sys.argv[9], filter_score_positive=sys.argv[10],
                                    select_id_name_action=sys.argv[11], filter_score_negative=sys.argv[12],
                                    filter_review_english=sys.argv[13], clients=sys.argv[14], porcentaje_por_ejecucion_para_cliente=sys.argv[15])
    elif query_input == "1":
        if len(sys.argv) != 8:
            print("Se debe ingresar: python generar_docker_compose.py <nombre_archivo_salida> <Queries> [FilterBasic] [SelectQ1] [PlatformCounter] [NumClients] [EjecucionesPorCliente]")
            sys.exit(1)
        generar_docker_compose(output_file=sys.argv[1], queries=queries, filterbasic=sys.argv[3], select_q1=sys.argv[4], platform_counter=sys.argv[5], clients=sys.argv[6], porcentaje_por_ejecucion_para_cliente=sys.argv[7])
    
    elif query_input == "2":
        if len(sys.argv) != 9:
            print("Se debe ingresar: python generar_docker_compose.py <nombre_archivo_salida> <Queries> [FilterBasic] [SelectQ2345] [FilterGender] [FilterDecade] [NumClients] [EjecucionesPorCliente]")
            sys.exit(1)
        generar_docker_compose(output_file=sys.argv[1], queries=queries, filterbasic=sys.argv[3], select_q2345=sys.argv[4], filter_gender=sys.argv[5],
                               filter_decade=sys.argv[6], clients=sys.argv[7], porcentaje_por_ejecucion_para_cliente=sys.argv[8])
    elif query_input == "3":
        if len(sys.argv) != 10:
            print("Se debe ingresar: python generar_docker_compose.py <nombre_archivo_salida> <Queries> [FilterBasic] [SelectQ2345] [FilterGender] [SelectIDNameIndie] [FilterScorePositive] [NumClients] [EjecucionesPorCliente]")
            sys.exit(1)
        generar_docker_compose(output_file=sys.argv[1], queries=queries, filterbasic=sys.argv[3], select_q2345=sys.argv[4], filter_gender=sys.argv[5],
                               select_id_name_indie=sys.argv[6], filter_score_positive=sys.argv[7], clients=sys.argv[8], porcentaje_por_ejecucion_para_cliente=sys.argv[9])
    elif query_input == "4":
        if len(sys.argv) != 11:
            print("Se debe ingresar: python generar_docker_compose.py <nombre_archivo_salida> <Queries> [FilterBasic] [SelectQ2345] [FilterGender] [SelectIDNameAction] [FilterScoreNegative] [FilterReviewEnglish] [NumClients] [EjecucionesPorCliente]")
            sys.exit(1)
        generar_docker_compose(output_file=sys.argv[1], queries=queries, filterbasic=sys.argv[3], select_q2345=sys.argv[4], filter_gender=sys.argv[5],
                               select_id_name_action=sys.argv[6], filter_score_negative=sys.argv[7], filter_review_english=sys.argv[8], clients=sys.argv[9], porcentaje_por_ejecucion_para_cliente=sys.argv[10])
    elif query_input == "5":
        if len(sys.argv) != 10:
            print("Se debe ingresar: python generar_docker_compose.py <nombre_archivo_salida> <Queries> [FilterBasic] [SelectQ2345] [FilterGender] [SelectIDNameAction] [FilterScoreNegative] [NumClients] [EjecucionesPorCliente]")
            sys.exit(1)
        generar_docker_compose(output_file=sys.argv[1], queries=queries, filterbasic=sys.argv[3], select_q2345=sys.argv[4], filter_gender=sys.argv[5],
                               select_id_name_action=sys.argv[6], filter_score_negative=sys.argv[7], clients=sys.argv[8], porcentaje_por_ejecucion_para_cliente=sys.argv[9])
    else:
        print("Invalid Query")
        sys.exit(1)