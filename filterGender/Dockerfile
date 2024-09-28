FROM python:3.9.20-alpine3.19
RUN apk update && apk add --no-cache python3-dev py3-pip
RUN pip install pika
COPY filterGender /app/filterGender
COPY common /app/common
ENTRYPOINT ["/bin/sh"]

