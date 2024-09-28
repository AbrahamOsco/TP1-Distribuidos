FROM python:3.9.20-alpine3.19
RUN apk update && apk add --no-cache python3-dev py3-pip
RUN pip install pika 
# TODO esto sacarlo, so el cliente no debe saber nada de pika esto las 2 lineas de antes hay q sacarlo 
COPY client /app/client
COPY common /app/common
ENTRYPOINT ["/bin/sh"]
