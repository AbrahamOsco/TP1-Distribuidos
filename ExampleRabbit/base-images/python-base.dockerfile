# Usar la imagen base de Python con Alpine
FROM python:3.9.20-alpine3.19

# Actualizar el gestor de paquetes e instalar pip
RUN apk update && apk add --no-cache python3-dev py3-pip

# Instalar pika usando pip
RUN pip install pika
