FROM python:3.9.20-alpine3.19
RUN apk update && apk add --no-cache python3-dev py3-pip
RUN pip install pika
COPY system/commonsSystem /app/system/commonsSystem
COPY system/controllers/gateway /app/system/controllers/gateway
COPY common /app/common
ENTRYPOINT ["/bin/sh"]

