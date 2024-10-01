import sys

def get_source(service_name):
    if service_name == "filterbasic":
        return "input_exchange"
    elif service_name == "selectq1" or service_name == "selectq2345" or service_name == "selectq345":
        return "filterbasic_exchange"
    elif service_name == "platformcounter":
        return "selectq1_exchange"
    elif service_name == "filtergender":
        return "selectq2345_exchange"
    elif service_name == "filterdecade" or service_name == "selectidname":
        return "filtergender_exchange"
    elif service_name == "filterreviewenglish" or service_name == "filterscorexpositive" or service_name == "filterscorenegative":
        return "selectq345_exchange"
    else:
        return "ERROR"

def generar_docker_compose(output_file, filter_basic, select_q1, platform_counter, select_q2345, filter_gender,
                           filter_decade, select_id_name, select_q345, filter_score_positive,
                           filter_review_english, filter_score_X_positives, filter_score_negative):
    compose_base = """
version: '3.8'

services:
  rabbitmq:
    container_name: rabbitmq
    image: rabbit:latest
    ports:
      - "5672:5672"  # Puerto para conexion con RabbitMQ
      - "15672:15672"  # Puerto para la interfaz de administracion
    networks:
      - system_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:15672"] # -f hace q curl falle silenciosamente si la web no funciona
      interval: 10s #verifica salud de rabbit each 10 s
      timeout: 5s # si rabbit no responde en 5s falla 
      retries: 10 # luego de 10 intentos => no es saludable

  client1:
    container_name: client1
    image: client:latest
    volumes:
      - ./data/games/games.csv:/data/games.csv
      - ./data/reviews/dataset.csv:/data/dataset.csv
    environment:
      - NODE_ID= 1
      - CLI_LOG_LEVEL= INFO
      - PYTHONPATH= /app  # le decimos a python que incluya /app para buscar paquetes asi podra encontrar el paquete client (/app/client). 
    entrypoint: python3 /app/client/main.py
    networks:
      - system_network
    restart: on-failure
    depends_on:
      rabbitmq:
        condition: service_healthy
      input:
        condition: service_started  # Puede esperar simplemente a que el sistema se haya iniciado    

  input:
    container_name: input
    build:
      context: .
      dockerfile: system/controllers/input/Dockerfile
    networks:
      - system_network
    depends_on:
      rabbitmq:
        condition: service_healthy
    environment:
      NODE_NAME: "input"
      NODE_ID: 2
      SOURCE: ""
      SINK: "input_exchange"
      LOGGING_LEVEL: INFO
      PYTHONPATH: /app

  output:
    container_name: output
    build:
      context: .
      dockerfile: system/controllers/output/Dockerfile
    networks:
      - system_network
    depends_on:
      rabbitmq:
        condition: service_healthy
    environment:
      NODE_NAME: "output"
      NODE_ID: 3
      SOURCE: "response_exchange"
      SINK: ""

  platformreducer:
    container_name: platformreducer
    build:
      context: .
      dockerfile: system/controllers/groupers/platformCounter/Dockerfile
    networks:
      - system_network
    depends_on:
      rabbitmq:
        condition: service_healthy
    environment:
      NODE_NAME: "platformreducer"
      NODE_ID: 4
      SOURCE: "platformcounter_exchange"
      SINK: "response_exchange"

  # sortertop10averageplaytime:
  #   container_name: sortertop10averageplaytime
  #   build:
  #     context: .
  #     dockerfile: sortertop10averageplaytime/Dockerfile
  #   networks:
  #     - system_network
  #   depends_on:
  #     - rabbitmq

  groupertopreviewspositiveindie:
    container_name: groupertopreviewspositiveindie
    build:
      context: .
      dockerfile: system/controllers/groupers/grouperTopReviewsPositiveIndie/Dockerfile
    networks:
      - system_network
    depends_on:
      rabbitmq:
        condition: service_healthy
    environment:
      NODE_NAME: "groupertopreviewspositiveindie"
      NODE_ID: 5
      SOURCE: ""
      SINK: ""
      

  # gamein90thpercentile:
  #   container_name: gamein90thpercentile
  #   build:
  #     context: .
  #     dockerfile: system/controllers/gamein90thpercentile/Dockerfile
  #   networks:
  #     - system_network
  #   depends_on:
  #     - rabbitmq
"""

    # Función para generar servicios
    def generar_servicios(tipo_servicio, nombre_servicio, cantidad):
        servicios = ""
        id = 5
        for i in range(1, int(cantidad) + 1):
            id += 1
            servicios += f"""
  {nombre_servicio.lower()}{"_"}{i}:
    container_name: {nombre_servicio.lower()}{"_"}{i}
    build:
      context: .
      dockerfile: system/controllers/{tipo_servicio}/{nombre_servicio}/Dockerfile
    networks:
      - system_network
    depends_on:
      rabbitmq:
        condition: service_healthy
    environment:
      NODE_NAME: {nombre_servicio.lower()}{"_"}{i}
      NODE_ID: {id}
      SOURCE: {get_source(nombre_servicio.lower())}
      SINK: {nombre_servicio.lower()}{"_exchange"}
"""
        return servicios

    # Generar los servicios correspondientes a cada parámetro
    client_services = generar_servicios("select","selectQ1", select_q1)
    client_services = generar_servicios("filters","filterBasic", filter_basic)
    client_services += generar_servicios("groupers","platformCounter", platform_counter)
    client_services += generar_servicios("select","selectQ2345", select_q2345)
    client_services += generar_servicios("filters","filterGender", filter_gender)
    client_services += generar_servicios("filters","filterDecade", filter_decade)
    client_services += generar_servicios("select","selectIDName", select_id_name)
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

    # Generar el contenido completo del archivo docker-compose
    docker_compose_content = compose_base + client_services + networks

    # Escribir en el archivo de salida
    with open(output_file, 'w') as f:
        f.write(docker_compose_content)

    print(f"{output_file} generado con los siguientes parámetros:")
    print(f"FilterBasic: {filter_basic}, SelectQ1: {select_q1}, PlatformCounter: {platform_counter}, "
          f"SelectQ2345: {select_q2345}, FilterGender: {filter_gender}, FilterDecade: {filter_decade}, "
          f"SelectIDName: {select_id_name}, SelectQ345: {select_q345}, "
          f"FilterScorePositive: {filter_score_positive}, FilterReviewEnglish: {filter_review_english}, "
          f"FilterScoreXPositives: {filter_score_X_positives}, FilterScoreNegative: {filter_score_negative}")

if __name__ == "__main__":
    if len(sys.argv) != 14:
        print("Se debe ingresar: python generar_docker_compose.py <nombre_archivo_salida> <FilterBasic> <SelectQ1> <PlatformCounter> <SelectQ2345> <FilterGender> <FilterDecade> <SelectIDName> <SelectQ345> <FilterScorePositive> <FilterReviewEnglish> <FilterScore50kPositives> <FilterScoreNegative>")
        sys.exit(1)

    # Capturar los parámetros desde la línea de comandos
    generar_docker_compose(*sys.argv[1:])