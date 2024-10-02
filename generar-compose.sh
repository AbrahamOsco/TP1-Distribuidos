#!/bin/bash

# Verificar que se hayan pasado los parámetros correctos
if [ "$#" -ne 1 ]; then
  echo "Se debe ingresar: $0 <nombre_archivo_salida>"
  exit 1
fi

# Función para verificar si una imagen existe
image_exists() {
  image_name=$1
  if [ "$(docker images -q $image_name)" ]; then
    return 0 # La imagen existe
  else
    return 1 # La imagen no existe
  fi
}

# Lista de las imágenes que se deben verificar
images=("rabbit:latest" "client:latest" "gateway:latest" \
        "selectq1:latest" "platformcounter:latest" \
        "selectq2345:latest" "filtergender:latest" "filterdecade:latest" \
        "selectidnameindie:latest" "selectidnameaction:latest" "selectq345:latest" \
        "filterscorepositive:latest" "filterreviewenglish:latest" "filterscorexpositives:latest" \
        "filterscorenegative:latest")

# Rutas específicas de los Dockerfiles de cada imagen
path_images=("system/rabbitmq" "client" "system/controllers/gateway"\
             "system/controllers/select/selectQ1" "system/controllers/groupers/platformCounter" \
             "system/controllers/select/selectQ2345" "system/controllers/filters/filterGender" "system/controllers/filters/filterDecade" \
             "system/controllers/select/selectIDNameIndie" "system/controllers/select/selectIDNameAction" "system/controllers/select/selectQ345" \
             "system/controllers/filters/filterScorePositive" "system/controllers/filters/filterReviewEnglish" "system/controllers/filters/filterScoreXPositives" \
             "system/controllers/filters/filterScoreNegative")

# Verificar si las imágenes existen, y si no, construirlas desde la ruta correspondiente
for i in "${!images[@]}"; do
  image="${images[$i]}"
  path="${path_images[$i]}"
  
  if ! image_exists "$image"; then
    echo "La imagen $image no existe. Creando desde $path..."
    docker build -t "$image" -f "$path"/Dockerfile .

  else
    echo "La imagen $image ya existe."
  fi
done

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
NUM_SELECT_Q1=$(solicitar_numero_entero "Ingrese la cantidad de SelectQ1: ")
NUM_PLATFORM_COUNTER=$(solicitar_numero_entero "Ingrese la cantidad de PlatformCounter: ")
NUM_SELECT_Q2345=$(solicitar_numero_entero "Ingrese la cantidad de SelectQ2345: ")
NUM_FILTER_GENDER=$(solicitar_numero_entero "Ingrese la cantidad de FilterGender: ")
NUM_FILTER_DECADE=$(solicitar_numero_entero "Ingrese la cantidad de FilterDecade: ")
NUM_SELECT_ID_NAME_INDIE=$(solicitar_numero_entero "Ingrese la cantidad de SelectIDNameIndie: ")
NUM_SELECT_ID_NAME_ACTION=$(solicitar_numero_entero "Ingrese la cantidad de SelectIDNameAction: ")
NUM_SELECT_Q345=$(solicitar_numero_entero "Ingrese la cantidad de SelectQ345: ")
NUM_FILTER_SCORE_POSITIVE=$(solicitar_numero_entero "Ingrese la cantidad de FilterScorePositive: ")
NUM_FILTER_REVIEW_ENGLISH=$(solicitar_numero_entero "Ingrese la cantidad de FilterReviewEnglish: ")
NUM_FILTER_SCORE_X_POSITIVES=$(solicitar_numero_entero "Ingrese la cantidad de FilterScoreXPositives: ")
NUM_FILTER_SCORE_NEGATIVE=$(solicitar_numero_entero "Ingrese la cantidad de FilterScoreNegative: ")

echo "Nombre del archivo de salida: $OUTPUT_FILE"
echo "Cantidad de SelectQ1: $NUM_SELECT_Q1"
echo "Cantidad de PlatformCounter: $NUM_PLATFORM_COUNTER"
echo "Cantidad de SelectQ2345: $NUM_SELECT_Q2345"
echo "Cantidad de FilterGender: $NUM_FILTER_GENDER"
echo "Cantidad de FilterDecade: $NUM_FILTER_DECADE"
echo "Cantidad de SelectIDNameIndie: $NUM_SELECT_ID_NAME_INDIE"
echo "Cantidad de SelectIDNameIndie: $NUM_SELECT_ID_NAME_ACTION"
echo "Cantidad de SelectQ345: $NUM_SELECT_Q345"
echo "Cantidad de FilterScorePositive: $NUM_FILTER_SCORE_POSITIVE"
echo "Cantidad de FilterReviewEnglish: $NUM_FILTER_REVIEW_ENGLISH"
echo "Cantidad de FilterScoreXPositives: $NUM_FILTER_SCORE_X_POSITIVES"
echo "Cantidad de FilterScoreNegative: $NUM_FILTER_SCORE_NEGATIVE"

# Llamar al script de Python para generar el archivo
python3 generar_docker_compose.py $OUTPUT_FILE \
    $NUM_SELECT_Q1 \
    $NUM_PLATFORM_COUNTER \
    $NUM_SELECT_Q2345 \
    $NUM_FILTER_GENDER \
    $NUM_FILTER_DECADE \
    $NUM_SELECT_ID_NAME_INDIE \
    $NUM_SELECT_ID_NAME_ACTION \
    $NUM_SELECT_Q345 \
    $NUM_FILTER_SCORE_POSITIVE \
    $NUM_FILTER_REVIEW_ENGLISH \
    $NUM_FILTER_SCORE_X_POSITIVES \
    $NUM_FILTER_SCORE_NEGATIVE

docker compose -f docker-compose-dev.yaml up -d
docker compose -f docker-compose-dev.yaml logs -f