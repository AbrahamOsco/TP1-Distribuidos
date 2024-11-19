FROM python:3.9.20-alpine3.19
RUN apk update && apk add --no-cache python3-dev py3-pip
RUN apk add docker
COPY common /app/common
COPY system/commonsSystem /app/system/commonsSystem
COPY system/leader /app/system/leader

ENTRYPOINT ["/bin/sh"]
