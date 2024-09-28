import sys

def generar_docker_compose(output_file, filter_basic, select_q1, platform_counter, select_q2345, filter_gender, filter_decade_2010):
    compose_base = """
services:
  server:
    container_name: server
    image: server:latest
    entrypoint: python3 /main.py
    volumes:
      - ./server/config.ini:/config.ini
    networks:
      - testing_net
"""

    # Función para generar servicios
    def generar_servicios(nombre_servicio, cantidad):
        servicios = ""
        for i in range(1, int(cantidad) + 1):
            servicios += f"""
  {nombre_servicio}{i}:
    container_name: {nombre_servicio}{i}
    image: {nombre_servicio}:latest
    entrypoint: /{nombre_servicio}
    environment:
      - ID={i}
    volumes:
      - ./{nombre_servicio}/config.yaml:/config.yaml
    networks:
      - testing_net
    depends_on:
      - server
"""
        return servicios

    # Generar los servicios correspondientes a cada parámetro
    client_services = generar_servicios("filter_basic", filter_basic)
    client_services += generar_servicios("select_q1", select_q1)
    client_services += generar_servicios("platform_counter", platform_counter)
    client_services += generar_servicios("select_q2345", select_q2345)
    client_services += generar_servicios("filter_gender", filter_gender)
    client_services += generar_servicios("filter_decade_2010", filter_decade_2010)

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
          f"SelectQ2345: {select_q2345}, FilterGender: {filter_gender}, FilterDecade2010: {filter_decade_2010}")

if __name__ == "__main__":
    if len(sys.argv) != 8:
        print("Se debe ingresar: python3 generar_docker_compose.py <nombre_archivo_salida> <FilterBasic> <SelectQ1> "
              "<PlatformCounter> <SelectQ2345> <FilterGender> <FilterDecade2010>")
        sys.exit(1)

    # Leer los argumentos de entrada
    output_file = sys.argv[1]
    filter_basic = sys.argv[2]
    select_q1 = sys.argv[3]
    platform_counter = sys.argv[4]
    select_q2345 = sys.argv[5]
    filter_gender = sys.argv[6]
    filter_decade_2010 = sys.argv[7]

    # Llamar a la función para generar el docker-compose
    generar_docker_compose(output_file, filter_basic, select_q1, platform_counter, select_q2345, filter_gender, filter_decade_2010)
