import sys

def generar_docker_compose(output_file, filter_basic, select_q1, platform_counter, select_q2345, filter_gender,
                           filter_decade_2010, select_id_name, select_q345, filter_score_positive,
                           filter_review_english, filter_score_50k_positives, filter_score_negative):
    compose_base = """
version: '3.8'

services:
  rabbitmq:
    container_name: rabbitmq
    image: rabbitmq:3-management
    ports:
      - "5672:5672"  # Puerto para conexion con RabbitMQ
      - "15672:15672"  # Puerto para la interfaz de administracion
    networks:
      - testing_net

  input:
    container_name: input
    build:
      context: ./input
      dockerfile: Dockerfile
    networks:
      - testing_net
    depends_on:
      - rabbitmq

  output:
    container_name: output
    build:
      context: ./output
      dockerfile: Dockerfile
    networks:
      - testing_net
    depends_on:
      - rabbitmq

  platformreducer:
    container_name: platformreducer
    build:
      context: ./platformreducer
      dockerfile: Dockerfile
    networks:
      - testing_net
    depends_on:
      - rabbitmq

  sortertop10averageplaytime:
    container_name: sortertop10averageplaytime
    build:
      context: ./sortertop10averageplaytime
      dockerfile: Dockerfile
    networks:
      - testing_net
    depends_on:
      - rabbitmq

  groupertop5reviewsposindie:
    container_name: groupertop5reviewsposindie
    build:
      context: ./groupertop5reviewsposindie
      dockerfile: Dockerfile
    networks:
      - testing_net
    depends_on:
      - rabbitmq

  gamein90thpercentile:
    container_name: gamein90thpercentile
    build:
      context: ./gamein90thpercentile
      dockerfile: Dockerfile
    networks:
      - testing_net
    depends_on:
      - rabbitmq
"""

    # Función para generar servicios
    def generar_servicios(nombre_servicio, cantidad):
        servicios = ""
        for i in range(1, int(cantidad) + 1):
            servicios += f"""
  {nombre_servicio.lower()}{"_"}{i}:
    container_name: {nombre_servicio.lower()}{"_"}{i}
    build:
      context: ./{nombre_servicio.lower()}
      dockerfile: Dockerfile
    networks:
      - testing_net
    depends_on:
      - rabbitmq
"""
        return servicios

    # Generar los servicios correspondientes a cada parámetro
    client_services = generar_servicios("FilterBasic", filter_basic)
    client_services += generar_servicios("SelectQ1", select_q1)
    client_services += generar_servicios("PlatformCounter", platform_counter)
    # client_services += generar_servicios("SelectQ2345", select_q2345)
    client_services += generar_servicios("FilterGender", filter_gender)
    client_services += generar_servicios("FilterDecade2010", filter_decade_2010)
    client_services += generar_servicios("SelectIDName", select_id_name)
    client_services += generar_servicios("SelectQ345", select_q345)
    client_services += generar_servicios("FilterScorePositive", filter_score_positive)
    client_services += generar_servicios("FilterReviewEnglish", filter_review_english)
    client_services += generar_servicios("FilterScore50kPositives", filter_score_50k_positives)
    client_services += generar_servicios("FilterScoreNegative", filter_score_negative)

    networks = """
networks:
  testing_net:
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
          f"SelectQ2345: {select_q2345}, FilterGender: {filter_gender}, FilterDecade2010: {filter_decade_2010}, "
          f"SelectIDName: {select_id_name}, SelectQ345: {select_q345}, "
          f"FilterScorePositive: {filter_score_positive}, FilterReviewEnglish: {filter_review_english}, "
          f"FilterScore50kPositives: {filter_score_50k_positives}, FilterScoreNegative: {filter_score_negative}")

if __name__ == "__main__":
    if len(sys.argv) != 14:
        print("Se debe ingresar: python generar_docker_compose.py <nombre_archivo_salida> <FilterBasic> <SelectQ1> <PlatformCounter> <SelectQ2345> <FilterGender> <FilterDecade2010> <SelectIDName> <SelectQ345> <FilterScorePositive> <FilterReviewEnglish> <FilterScore50kPositives> <FilterScoreNegative>")
        sys.exit(1)

    # Capturar los parámetros desde la línea de comandos
    generar_docker_compose(*sys.argv[1:])
