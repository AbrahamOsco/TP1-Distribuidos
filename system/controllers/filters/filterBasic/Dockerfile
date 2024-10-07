FROM python:3.9.20-alpine3.19
RUN apk update && apk add --no-cache python3-dev py3-pip
RUN pip install pika
COPY common /app/common
COPY system/commonsSystem /app/system/commonsSystem
COPY system/controllers/filters/filterBasic /app/system/controllers/filters/filterBasic
ENTRYPOINT ["/bin/sh"]

