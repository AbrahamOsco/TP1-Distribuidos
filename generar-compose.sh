#!/bin/bash

# Verificar que se hayan pasado los parámetros correctos
if [ "$#" -ne 1 ]; then
  echo "Se debe ingresar: $0 <nombre_archivo_salida>"
  exit 1
fi

# Parámetro de salida
OUTPUT_FILE=$1

# Función para validar que la entrada sea un número entero
function solicitar_numero_entero() {
  local mensaje=$1
  local numero
  while true; do
    read -p "$mensaje" numero
    if [[ "$numero" =~ ^[0-9]+$ ]]; then
      echo $numero
      return
    else
      echo "Error: La entrada debe ser un número entero."
    fi
  done
}

# Solicitar las cantidades para cada tipo de servicio
NUM_FILTER_BASIC=$(solicitar_numero_entero "Ingrese la cantidad de FilterBasic: ")
NUM_SELECT_Q1=$(solicitar_numero_entero "Ingrese la cantidad de SelectQ1: ")
NUM_PLATFORM_COUNTER=$(solicitar_numero_entero "Ingrese la cantidad de PlatformCounter: ")
NUM_SELECT_Q2345=$(solicitar_numero_entero "Ingrese la cantidad de SelectQ2345: ")
NUM_FILTER_GENDER=$(solicitar_numero_entero "Ingrese la cantidad de FilterGender: ")
NUM_FILTER_DECADE_2010=$(solicitar_numero_entero "Ingrese la cantidad de FilterDecade2010: ")
NUM_SELECT_ID_NAME=$(solicitar_numero_entero "Ingrese la cantidad de SelectIDName: ")
NUM_SELECT_Q345=$(solicitar_numero_entero "Ingrese la cantidad de SelectQ345: ")
NUM_FILTER_SCORE_POSITIVE=$(solicitar_numero_entero "Ingrese la cantidad de FilterScorePositive: ")
NUM_FILTER_REVIEW_ENGLISH=$(solicitar_numero_entero "Ingrese la cantidad de FilterReviewEnglish: ")
NUM_FILTER_SCORE_50K_POSITIVES=$(solicitar_numero_entero "Ingrese la cantidad de FilterScore50kPositives: ")
NUM_FILTER_SCORE_NEGATIVE=$(solicitar_numero_entero "Ingrese la cantidad de FilterScoreNegative: ")

echo "Nombre del archivo de salida: $OUTPUT_FILE"
echo "Cantidad de FilterBasic: $NUM_FILTER_BASIC"
echo "Cantidad de SelectQ1: $NUM_SELECT_Q1"
echo "Cantidad de PlatformCounter: $NUM_PLATFORM_COUNTER"
echo "Cantidad de SelectQ2345: $NUM_SELECT_Q2345"
echo "Cantidad de FilterGender: $NUM_FILTER_GENDER"
echo "Cantidad de FilterDecade2010: $NUM_FILTER_DECADE_2010"
echo "Cantidad de SelectIDName: $NUM_SELECT_ID_NAME"
echo "Cantidad de SelectQ345: $NUM_SELECT_Q345"
echo "Cantidad de FilterScorePositive: $NUM_FILTER_SCORE_POSITIVE"
echo "Cantidad de FilterReviewEnglish: $NUM_FILTER_REVIEW_ENGLISH"
echo "Cantidad de FilterScore50kPositives: $NUM_FILTER_SCORE_50K_POSITIVES"
echo "Cantidad de FilterScoreNegative: $NUM_FILTER_SCORE_NEGATIVE"

# Llamar al script de Python para generar el archivo
python generar_docker_compose.py $OUTPUT_FILE \
    $NUM_FILTER_BASIC \
    $NUM_SELECT_Q1 \
    $NUM_PLATFORM_COUNTER \
    $NUM_SELECT_Q2345 \
    $NUM_FILTER_GENDER \
    $NUM_FILTER_DECADE_2010 \
    $NUM_SELECT_ID_NAME \
    $NUM_SELECT_Q345 \
    $NUM_FILTER_SCORE_POSITIVE \
    $NUM_FILTER_REVIEW_ENGLISH \
    $NUM_FILTER_SCORE_50K_POSITIVES \
    $NUM_FILTER_SCORE_NEGATIVE
