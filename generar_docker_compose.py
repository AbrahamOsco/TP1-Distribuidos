import sys

def get_source(service_name):
    if service_name == "filterbasic":
        return "DataRaw"
    elif service_name == "selectq1" or service_name == "selectq2345" or service_name == "selectq345":
        return "DataParsed"
    elif service_name == "platformcounter":
        return "GamesPlatform"
    elif service_name == "filtergender":
        return "GamesQ2345"
    elif service_name == "filterdecade":
        return "GamesIndieQ2"
    elif service_name == "selectidnameindie":
        return "GamesIndieQ3"
    elif service_name == "monitorstorageq3":
        return "GamesIndieQ3Sumarized"
    elif service_name == "groupertopreviewspos":
        return "GamesIndieMonitor"
    elif service_name == "selectidnameaction":
        return "GamesActionQ45"
    elif service_name == "monitorjoinerq4" or service_name == "monitorstorageq5":
        return "GamesActionQ45Sumarized"
    elif service_name == "filterreviewenglish":
        return "GamesActionPositives"
    elif service_name == "filterscorexpositive" or service_name == "filterscorenegative":
        return "ReviewsRaw"
    elif service_name == "output":
        return "ClientsResponse"
    else:
        return "ERROR"

def get_sink(service_name):
    if service_name == "gateway":
        return "DataParsed"
    elif service_name == "selectq1":
        return "GamesPlatform"
    elif service_name == "platformcounter":
        return "countbyplatform"
    elif service_name == "selectq2345":
        return "GamesQ2345"
    elif service_name == "filtergenderindieq2":
        return "GamesIndieQ2"
    elif service_name == "filterdecade":
        return "GamesIndieDecadeQ2"
    elif service_name == "filtergenderindieq3":
        return "GamesIndieQ3"
    elif service_name == "selectidnameindie":
        return "GamesIndieQ3Sumarized"
    elif service_name == "monitorstorageq3":
        return "GamesIndieMonitor"
    elif service_name == "filtergenderactionq45":
        return "GamesActionQ45"
    elif service_name == "selectidnameaction":
        return "GamesActionQ45Sumarized"
    elif service_name == "monitorjoinerq4":
        return "GamesActionPositives"
    elif service_name == "filterreviewenglish":
        return "ReviewsEnglishPositives"
    elif service_name == "filterscorexpositive":
        return "ReviewsPositives"
    elif service_name == "filterscorenegative":
        return "ReviewsNegatives"
    elif service_name == "monitorstorageq4" or service_name == "monitorstorageq5" or service_name == "platformreducer" or service_name == "groupertopaverageplaytime" or service_name == "groupertopreviewspos":
        return "ClientsResponse"
    else:
        return "ERROR"

def generar_docker_compose(output_file, filter_basic, select_q1, platform_counter, select_q2345, filter_gender,
                           filter_decade, select_id_name_indie, select_id_name_action, select_q345, filter_score_positive,
                           filter_review_english, filter_score_X_positives, filter_score_negative):
    compose_base = """
version: '3.8'

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

  client1:
    container_name: client1
    image: client:latest
    entrypoint: python3 /app/client/main.py
    volumes:
      - ./data/games/games.csv:/data/games.csv
      - ./data/reviews/dataset.csv:/data/dataset.csv
    environment:
      - NODE_ID=1
      - LOGGING_LEVEL=INFO
      - PYTHONPATH=/app
      - AMOUNT_NEEDED=1
      - AMOUNT_OF_NODES=1
      - TOP_SIZE=5
      - HOSTNAME="localhost"
    networks:
      - system_network
    restart: on-failure
    depends_on:
      rabbitmq:
        condition: service_healthy

  gateway:
    container_name: gateway
    image: gateway:latest
    entrypoint: python3 /app/system/controllers/gateway/main.py
    networks:
      - system_network
    restart: on-failure
    depends_on:
      rabbitmq:
        condition: service_healthy
    environment:
      - NODE_NAME:"gateway"
      - NODE_ID=2
      - SOURCE=""
      - SINK=""
      - LOGGING_LEVEL=INFO
      - PYTHONPATH=/app
      - AMOUNT_NEEDED=1
      - AMOUNT_OF_NODES=1
      - TOP_SIZE=5
"""
    def generar_servicios(tipo_servicio, nombre_servicio, cantidad):
        servicios = ""
        id = 5
        for i in range(1, int(cantidad) + 1):
            id += 1
            servicios += f"""
  {nombre_servicio.lower()}{"_"}{i}:
    container_name: {nombre_servicio.lower()}{"_"}{i}
    image: {nombre_servicio.lower()}:latest
    entrypoint: python3 /app/system/controllers/{tipo_servicio}/{nombre_servicio}/main.py
    networks:
      - system_network
    restart: on-failure
    depends_on:
      rabbitmq:
        condition: service_healthy
    environment:
      - NODE_NAME="{nombre_servicio.lower()}{"_"}{i}"
      - NODE_ID={id}
      - SOURCE={get_source(nombre_servicio.lower())}
      - SINK={get_sink(nombre_servicio.lower())}
      - LOGGING_LEVEL=INFO
      - PYTHONPATH=/app
      - AMOUNT_NEEDED={cantidad}
      - DECADE=2010
      - AMOUNT_OF_NODES={cantidad}
      - GENDERS="Action,Indie"
      - TOP_SIZE=5
"""
        return servicios

    client_services = generar_servicios("select","selectQ1", select_q1)
    client_services += generar_servicios("filters","filterBasic", filter_basic)
    client_services += generar_servicios("groupers","platformCounter", platform_counter)
    client_services += generar_servicios("select","selectQ2345", select_q2345)
    client_services += generar_servicios("filters","filterGender", filter_gender)
    client_services += generar_servicios("filters","filterDecade", filter_decade)
    client_services += generar_servicios("select","selectIDNameIndie", select_id_name_indie)
    client_services += generar_servicios("select","selectIDNameAction", select_id_name_action)
    client_services += generar_servicios("select","selectQ345", select_q345)
    client_services += generar_servicios("filters","filterScorePositive", filter_score_positive)
    client_services += generar_servicios("filters","filterReviewEnglish", filter_review_english)
    client_services += generar_servicios("filters","filterScoreXPositives", filter_score_X_positives)
    client_services += generar_servicios("filters","filterScoreNegative", filter_score_negative)

    networks = """
networks:
  system_network:
    ipam:
      driver: default
      config:
        - subnet: 172.25.125.0/24
"""

    docker_compose_content = compose_base + client_services + networks

    with open(output_file, 'w') as f:
        f.write(docker_compose_content)

    print(f"{output_file} generado con los siguientes parámetros:")
    print(f"FilterBasic: {filter_basic}, SelectQ1: {select_q1}, PlatformCounter: {platform_counter}, "
          f"SelectQ2345: {select_q2345}, FilterGender: {filter_gender}, FilterDecade: {filter_decade}, "
          f"SelectIDNameIndie: {select_id_name_indie}, SelectIDNameAction: {select_id_name_action}, SelectQ345: {select_q345}, "
          f"FilterScorePositive: {filter_score_positive}, FilterReviewEnglish: {filter_review_english}, "
          f"FilterScoreXPositives: {filter_score_X_positives}, FilterScoreNegative: {filter_score_negative}")

if __name__ == "__main__":
    if len(sys.argv) != 15:
        print("Se debe ingresar: python generar_docker_compose.py <nombre_archivo_salida> <FilterBasic> <SelectQ1> <PlatformCounter> <SelectQ2345> <FilterGender> <FilterDecade> <SelectIDNameIndie> <SelectIDNameAction> <SelectQ345> <FilterScorePositive> <FilterReviewEnglish> <FilterScore50kPositives> <FilterScoreNegative>")
        sys.exit(1)

    generar_docker_compose(*sys.argv[1:])
