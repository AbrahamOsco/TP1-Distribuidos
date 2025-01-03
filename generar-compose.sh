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

# Función para validar que la entrada sea un número entero mayor o igual a un valor dado
function solicitar_numero_entero_con_minimo() {
  local mensaje=$1
  local minimo=$2
  local numero
  while true; do
    read -p "$mensaje" numero
    if [[ "$numero" =~ ^[0-9]+$ ]] && [ "$numero" -ge "$minimo" ]; then
      echo $numero
      return
    else
      echo "Error: La entrada debe ser un número entero mayor o igual a $minimo."
    fi
  done
}

# Función para validar que la entrada sea S o N
function solicitar_si_no() {
  local mensaje=$1
  local respuesta
  while true; do
    read -p "$mensaje" respuesta
    if [[ "$respuesta" =~ ^[SN]$ ]]; then
      echo $respuesta
      return
    else
      echo "Error: La entrada debe ser un S(sí) o N(no)."
    fi
  done
}

# Función para validar que la entrada sea un array de porcentajes permitidos (0.1, 0.2, 0.3, 0.4, 0.5, 1)
function solicitar_porcentajes() {
  local mensaje=$1
  local porcentajes
  while true; do
    read -p "$mensaje" porcentajes
    if [[ "$porcentajes" =~ ^(0\.[1-5]|1)(,(0\.[1-5]|1))*$ ]]; then
      echo $porcentajes
      return
    fi
  done
}

NUM_CLIENTS=$(solicitar_numero_entero "Ingrese la cantidad de clientes: ")

# Solicitar la cantidad de ejecuciones por cliente y los porcentajes correspondientes
declare -a porcentajes_por_cliente
for ((i = 1; i <= NUM_CLIENTS; i++)); do
  porcentajes_por_cliente[$i]=$(solicitar_porcentajes "Ingrese los porcentajes para el cliente $i (por ejemplo, 0.1,0.2,0.3 o todo el archivo: 1): ")
done

# Solicitar las cantidades para cada tipo de servicio
ALL_QUERIES=$(solicitar_si_no "¿Desea ejecutar todas las consultas? (S/N): ")
QUERIES=""
if [ "$ALL_QUERIES" == "S" ]; then
  QUERIES="A"
else
  QUERIES=$(solicitar_numero_entero "Ingrese el numero de la query a ejecutar: ")
fi
ESCALATE=$(solicitar_si_no "¿Desea seleccionar cantidad de nodos? (S/N): ")
if [ "$ESCALATE" == "S" ]; then
  NUM_FILTER_BASIC=$(solicitar_numero_entero "Ingrese la cantidad de FilterBasic: ")
  if [ "$QUERIES" == "A" ] || [[ "$QUERIES" == *"1"* ]]; then
    NUM_SELECT_Q1=$(solicitar_numero_entero "Ingrese la cantidad de SelectQ1: ")
    NUM_PLATFORM_COUNTER=$(solicitar_numero_entero "Ingrese la cantidad de PlatformCounter: ")
  fi
  if [ "$QUERIES" == "A" ] || [[ "$QUERIES" == *"2"* ]] || [[ "$QUERIES" == *"3"* ]] || [[ "$QUERIES" == *"4"* ]] || [[ "$QUERIES" == *"5"* ]]; then
    NUM_SELECT_Q2345=$(solicitar_numero_entero "Ingrese la cantidad de SelectQ2345: ")
    NUM_FILTER_GENDER=$(solicitar_numero_entero "Ingrese la cantidad de FilterGender: ")
  fi
  if [ "$QUERIES" == "A" ] || [[ "$QUERIES" == *"2"* ]]; then
    NUM_FILTER_DECADE=$(solicitar_numero_entero "Ingrese la cantidad de FilterDecade: ")
  fi
  if [ "$QUERIES" == "A" ] || [[ "$QUERIES" == *"3"* ]]; then
    NUM_SELECT_ID_NAME_INDIE=$(solicitar_numero_entero "Ingrese la cantidad de SelectIDNameIndie: ")
    NUM_FILTER_SCORE_POSITIVE=$(solicitar_numero_entero "Ingrese la cantidad de FilterScorePositive: ")
  fi
  if [ "$QUERIES" == "A" ] || [[ "$QUERIES" == *"4"* ]] || [[ "$QUERIES" == *"5"* ]]; then
    NUM_SELECT_ID_NAME_ACTION=$(solicitar_numero_entero "Ingrese la cantidad de SelectIDNameAction: ")
    NUM_FILTER_SCORE_NEGATIVE=$(solicitar_numero_entero "Ingrese la cantidad de FilterScoreNegative: ")
  fi
  if [ "$QUERIES" == "A" ] || [[ "$QUERIES" == *"4"* ]]; then
    NUM_FILTER_REVIEW_ENGLISH=$(solicitar_numero_entero "Ingrese la cantidad de FilterReviewEnglish: ")
  fi
else
  NUM_FILTER_BASIC=1
  NUM_SELECT_Q1=1
  NUM_PLATFORM_COUNTER=1
  NUM_SELECT_Q2345=1
  NUM_FILTER_GENDER=1
  NUM_FILTER_DECADE=1
  NUM_SELECT_ID_NAME_INDIE=1
  NUM_FILTER_SCORE_POSITIVE=1
  NUM_SELECT_ID_NAME_ACTION=1
  NUM_FILTER_SCORE_NEGATIVE=1
  NUM_FILTER_REVIEW_ENGLISH=1
fi

# Modificar la forma en que se pasan los porcentajes por cliente
PORCENTAJES_CLIENTES=$(IFS=\;; echo "${porcentajes_por_cliente[*]}")

if [ "$QUERIES" == "A" ]; then
  python3 generar_docker_compose.py $OUTPUT_FILE \
      $QUERIES \
      $NUM_FILTER_BASIC \
      $NUM_SELECT_Q1 \
      $NUM_PLATFORM_COUNTER \
      $NUM_SELECT_Q2345 \
      $NUM_FILTER_GENDER \
      $NUM_FILTER_DECADE \
      $NUM_SELECT_ID_NAME_INDIE \
      $NUM_FILTER_SCORE_POSITIVE \
      $NUM_SELECT_ID_NAME_ACTION \
      $NUM_FILTER_SCORE_NEGATIVE \
      $NUM_FILTER_REVIEW_ENGLISH \
      $NUM_CLIENTS \
      "$PORCENTAJES_CLIENTES"
elif [[ "$QUERIES" == *"1"* ]]; then
  python3 generar_docker_compose.py $OUTPUT_FILE \
      $QUERIES \
      $NUM_FILTER_BASIC \
      $NUM_SELECT_Q1 \
      $NUM_PLATFORM_COUNTER \
      $NUM_CLIENTS \
      "$PORCENTAJES_CLIENTES"
elif [[ "$QUERIES" == *"2"* ]]; then
  python3 generar_docker_compose.py $OUTPUT_FILE \
      $QUERIES \
      $NUM_FILTER_BASIC \
      $NUM_SELECT_Q2345 \
      $NUM_FILTER_GENDER \
      $NUM_FILTER_DECADE \
      $NUM_CLIENTS \
      "$PORCENTAJES_CLIENTES"
elif [[ "$QUERIES" == *"3"* ]]; then
  python3 generar_docker_compose.py $OUTPUT_FILE \
      $QUERIES \
      $NUM_FILTER_BASIC \
      $NUM_SELECT_Q2345 \
      $NUM_FILTER_GENDER \
      $NUM_SELECT_ID_NAME_INDIE \
      $NUM_FILTER_SCORE_POSITIVE \
      $NUM_CLIENTS \
      "$PORCENTAJES_CLIENTES"
elif [[ "$QUERIES" == *"4"* ]]; then
  python3 generar_docker_compose.py $OUTPUT_FILE \
      $QUERIES \
      $NUM_FILTER_BASIC \
      $NUM_SELECT_Q2345 \
      $NUM_FILTER_GENDER \
      $NUM_SELECT_ID_NAME_ACTION \
      $NUM_FILTER_SCORE_NEGATIVE \
      $NUM_FILTER_REVIEW_ENGLISH \
      $NUM_CLIENTS \
      "$PORCENTAJES_CLIENTES"
elif [[ "$QUERIES" == *"5"* ]]; then
  python3 generar_docker_compose.py $OUTPUT_FILE \
      $QUERIES \
      $NUM_FILTER_BASIC \
      $NUM_SELECT_Q2345 \
      $NUM_FILTER_GENDER \
      $NUM_SELECT_ID_NAME_ACTION \
      $NUM_FILTER_SCORE_NEGATIVE \
      $NUM_CLIENTS \
      "$PORCENTAJES_CLIENTES"
fi
