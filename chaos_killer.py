import random
import subprocess
import time
import sys
import threading
from datetime import datetime
import os

LOG_FILE = "chaos_killer.log"

def inicializar_log():
    """Crea el archivo de log si no existe y añade un separador para cada nueva ejecucion."""
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as log_file:
            log_file.write("=== Chaos Killer Log Iniciado ===\n")
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"\n=== Nueva ejecucion: {datetime.now()} ===\n")

def escribir_log(mensaje):
    """Escribe un mensaje en el archivo de log."""
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{datetime.now()} - {mensaje}\n")

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
        escribir_log(f"Contenedor {contenedor} ha sido revivido")
    except subprocess.CalledProcessError as e:
        print(f"Error al revivir el contenedor {contenedor}: {e}")
        escribir_log(f"Error al revivir el contenedor {contenedor}: {e}")

def obtener_contenedores_vivos():
    try:
        resultado = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True, text=True, check=True
        )
        contenedores = [
            nombre for nombre in resultado.stdout.splitlines()
            if nombre != "rabbitmq" and not nombre.startswith("client")
        ]
        return contenedores
    except subprocess.CalledProcessError as e:
        print(f"Error al obtener contenedores vivos: {e}")
        escribir_log(f"Error al obtener contenedores vivos: {e}")
        return []

def matar_contenedor(contenedor):
    try:
        subprocess.run(
            ["docker", "kill", "--signal=SIGKILL", contenedor],
            check=True
        )
        print(f"Contenedor {contenedor} ha sido matado")
        escribir_log(f"Contenedor {contenedor} ha sido matado con SIGKILL")
    except subprocess.CalledProcessError as e:
        print(f"Error al matar el contenedor {contenedor}: {e}")
        escribir_log(f"Error al matar el contenedor {contenedor}: {e}")

def chaos_killer(intervalo, auto_revive):
    while True:
        contenedores = obtener_contenedores_vivos()
        
        if contenedores:
            contenedor = random.choice(contenedores)
            print(f"Seleccionando contenedor {contenedor} para matar...")
            escribir_log(f"Seleccionando contenedor {contenedor} para matar...")
            
            matar_contenedor(contenedor)
            if auto_revive:
                revivir_contenedor(contenedor)
        else:
            print("No hay contenedores vivos en este momento.")
            escribir_log("No hay contenedores vivos en este momento.")
        
        time.sleep(intervalo)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python3 chaos_killer.py <intervalo_en_segundos> <auto_revive>")
        sys.exit(1)

    intervalo_tiempo = int(sys.argv[1])
    auto_revive = bool(int(sys.argv[2]))

    inicializar_log()
    chaos_killer(intervalo_tiempo, auto_revive)
