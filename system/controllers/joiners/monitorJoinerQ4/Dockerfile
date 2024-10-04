FROM python:3.9.20-alpine3.19
RUN apk update && apk add --no-cache python3-dev py3-pip
RUN pip install pika
COPY system/controllers/joiners/monitorJoinerQ4 /app/system/controllers/joiners/monitorJoinerQ4
COPY system/commonsSystem /app/system/commonsSystem
COPY common /app/common
ENTRYPOINT ["/bin/sh"]

