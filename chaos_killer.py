import random
import subprocess
import time
import sys
import threading

def revivir_contenedor(contenedor):
    threading.Thread(target=revivir_contenedor_thread, args=(contenedor,)).start()

def revivir_contenedor_thread(contenedor):
    try:
        time.sleep(8)
        subprocess.run(
            ["docker", "start", contenedor],
            check=True
        )
        print(f"Contenedor {contenedor} ha sido revivido")
    except subprocess.CalledProcessError as e:
        print(f"Error al revivir el contenedor {contenedor}: {e}")

# Función para obtener una lista de contenedores en ejecución, excepto "rabbitmq" y los que empiecen con "client"
def obtener_contenedores_vivos():
    try:
        # Ejecuta el comando para obtener los contenedores vivos
        resultado = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True, text=True, check=True
        )
<<<<<<< HEAD
        # Filtrar los contenedores que no se llamen "rabbitmq" ni empiecen con "client#"
        contenedores = [
            nombre for nombre in resultado.stdout.splitlines()
            if nombre != "rabbitmq" and not nombre.startswith("client")
        ]
=======

        # Filtrar los contenedores que no se llamen "rabbitmq"
        contenedores = [nombre for nombre in resultado.stdout.splitlines() if nombre != "rabbitmq" and not nombre.startswith("client")]
>>>>>>> 2a0bb54 (fix conflcit in chaos_kller.py)
        return contenedores
    except subprocess.CalledProcessError as e:
        print(f"Error al obtener contenedores vivos: {e}")
        return []

# Función para matar un contenedor completo usando 'docker kill'
def matar_contenedor(contenedor):
    try:
        subprocess.run(
            ["docker", "kill", "--signal=SIGKILL", contenedor],
            check=True
        )
        print(f"Contenedor {contenedor} ha sido matado")
    except subprocess.CalledProcessError as e:
        print(f"Error al matar el contenedor {contenedor}: {e}")

# Función principal que mata contenedores aleatoriamente periódicamente
def chaos_killer(intervalo, auto_revive):
    while True:
        # Obtener los contenedores vivos excluyendo "rabbitmq"
        contenedores = obtener_contenedores_vivos()
        
        if contenedores:
            # Elegir un contenedor aleatoriamente
            contenedor = random.choice(contenedores)
            print(f"Seleccionando contenedor {contenedor} para matar...")

            # Matar el contenedor seleccionado
            matar_contenedor(contenedor)
            if auto_revive:
                revivir_contenedor(contenedor)
        else:
            print("No hay contenedores vivos en este momento.")
        
        # Esperar el intervalo antes de repetir
        time.sleep(intervalo)

# Comprobar si se ha pasado el intervalo como argumento
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python3 chaos_killer.py <intervalo_en_segundos> <auto_revive>")
        sys.exit(1)

    # Convertir el argumento a un entero
    intervalo_tiempo = int(sys.argv[1])
    #auto_revive = int(sys.argv[2])

    # Ejecutar el chaos killer con el intervalo proporcionado
    chaos_killer(intervalo_tiempo, None)
