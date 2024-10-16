import sys

node_id = 3

def generate_network():
  return """
networks:
  system_network:
    ipam:
      driver: default
      config:
        - subnet: 172.25.125.0/24
"""

def add_top_size(top_size):
  return f"""
      - TOP_SIZE={top_size}"""

def generate_services(name_service, count, image, entrypoint_path, top_size = 0):
    services = ""
    top_enviroment = ""
    global node_id
    node_id_current = node_id
    if top_size !=0 : 
      top_enviroment = add_top_size(top_size)
    for i in range(0, count):
        node_id_current = node_id
        node_id_current = node_id_current + (i)
        service = f"""\n  {name_service}_{i+1}:
    container_name: {name_service}_{i+1}
    image: {image}
    entrypoint: python3 {entrypoint_path}
    environment:
      - LOGGING_LEVEL=INFO
      - PYTHONPATH=/app
      - NODE_ID={node_id_current}
      - TOTAL_NODES={count} {top_enviroment}
    networks:
      - system_network
    depends_on:
      rabbitmq:
        condition: service_healthy
"""
        services += service
    node_id += count
    return services

def get_compose_query1():
  compose_query_1 = generate_services("filterbasic", 3, "filterbasic:latest", "/app/system/controllers/filters/filterBasic/main.py")
  compose_query_1 += generate_services("selectq1", 3, "selectq1:latest", "/app/system/controllers/select/selectQ1/main.py")
  compose_query_1 += generate_services("platformcounter", 2, "platformcounter:latest", "/app/system/controllers/groupers/platformCounter/main.py")
  compose_query_1 += generate_services("platformreducer", 1, "platformreducer:latest", "/app/system/controllers/reducers/platformReducer/main.py")
  return compose_query_1

def get_compose_query2():
  compose_query_2 = generate_services("selectq2345", 3, "selectq2345:latest", "/app/system/controllers/select/selectQ2345/main.py")
  compose_query_2 += generate_services("filtergender", 3, "filtergender:latest", "/app/system/controllers/filters/filterGender/main.py")
  compose_query_2 += generate_services("filterdecade", 2, "filterdecade:latest", "/app/system/controllers/filters/filterDecade/main.py")
  compose_query_2 += generate_services("groupertopavgplaytime", 1, "groupertopavgplaytime:latest", "/app/system/controllers/groupers/grouperTopAvgPlaytime/main.py", 10)
  return compose_query_2

def get_compose_query3():
  compose_query_3 = generate_services("filterscorepositive", 3, "filterscorepositive:latest", "/app/system/controllers/filters/filterScorePositive/main.py")
  compose_query_3 += generate_services("selectidname", 3, "selectidname:latest", "/app/system/controllers/select/selectIDName/main.py")
  compose_query_3 += generate_services("monitorstorageq3", 1, "monitorstorageq3:latest", "/app/system/controllers/storages/monitorStorageQ3/main.py")
  compose_query_3 += generate_services("groupertoppositivereviews", 1, "groupertoppositivereviews:latest", "/app/system/controllers/groupers/grouperTopReviewsPositiveIndie/main.py", 5)
  return compose_query_3

def get_compose_query4():
  compose_query_4 = generate_services("filterscorenegative", 2, "filterscorenegative:latest", "/app/system/controllers/filters/filterScoreNegative/main.py")
  compose_query_4 += generate_services("monitorstorageq4", 1, "monitorstorageq4:latest", "/app/system/controllers/storages/monitorStorageQ4/main.py")
  compose_query_4 += generate_services("filterreviewsenglish", 1, "filterreviewsenglish:latest", "/app/system/controllers/filters/filterReviewsEnglish/main.py")
  return compose_query_4

def get_compose_query5():
  compose_query_5 = generate_services("monitorstorageq5", 1, "monitorstorageq5:latest", "/app/system/controllers/storages/monitorStorageQ5/main.py")
  compose_query_5 += generate_services("grouperpercentile", 1, "grouperpercentile:latest", "/app/system/controllers/groupers/grouperPercentile/main.py")
  return compose_query_5


def generar_docker_compose_basic(amount_queries):
  docker_compose_content = """version: '3.8'
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
    entrypoint: python3 /app/client/main.py
    volumes:
      - ./data/games.csv:/data/games.csv
      - ./data/dataset.csv:/data/dataset.csv
      - ./resultsExpect:/resultsExpect
      - ./results:/results
    environment:
      - NODE_ID=1
      - LOGGING_LEVEL=INFO
      - PYTHONPATH=/app
      - HOSTNAME=gateway
      - PERCENT_OF_FILE_FOR_USE=0.1
    networks:
      - system_network
    depends_on:
      rabbitmq:
        condition: service_healthy
      gateway:
        condition: service_started

  gateway:
    container_name: gateway
    image: gateway:latest
    entrypoint: python3 /app/system/controllers/gateway/main.py 
    environment:
      - LOGGING_LEVEL=INFO
      - PYTHONPATH=/app
      - NODE_ID=2
    networks:
      - system_network
    depends_on:
      rabbitmq:
        condition: service_healthy  # Espera hasta que RabbitMQ esté saludable
"""
  docker_compose_content += get_compose_query1()
  if amount_queries >=2: 
    docker_compose_content += get_compose_query2()
  if amount_queries >=3:
    docker_compose_content += get_compose_query3()
  if amount_queries >=4:
    docker_compose_content += get_compose_query4()
  if amount_queries >=5:
    docker_compose_content += get_compose_query5()
  
  docker_compose_content += generate_network()

  with open('new_docker_compose.yaml', 'w') as file:
    file.write(docker_compose_content)
  print("Archivo new_docker_compose.yaml creado con éxito.")


if __name__ == "__main__":
  argc = len(sys.argv)  # Cantidad de argumentos pasados (incluido el nombre del script)
  print(f"sys.argv: {sys.argv}")
  if argc < 2:
    print("Por favor, pasa la cantidad de consultas como argumento.")
    sys.exit(1)
  amount_queries = int(sys.argv[1])
  generar_docker_compose_basic(amount_queries)

