#!/bin/bash

# Ruta del archivo de configuración
CONFIG_FILE="chaos_killer.conf"

# Leer el archivo de configuración y obtener el intervalo de tiempo
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
    echo "Intervalo de tiempo configurado: $INTERVALO_TIEMPO segundos. Auto Revive: $AUTO_REVIVE"
else
    echo "Archivo de configuración no encontrado. Asegúrate de que $CONFIG_FILE existe."
    exit 1
fi

# Ejecutar el script de Python con el intervalo configurado
python3 chaos_killer.py "$INTERVALO_TIEMPO" "$AUTO_REVIVE"
