FROM python:3.9.20-alpine3.19
RUN apk update && apk add --no-cache python3-dev py3-pip
COPY common /app/common
COPY system/commonsSystem/utils /app/system/commonsSystem/utils
COPY system/leader /app/system/leader

ENTRYPOINT ["/bin/sh"]
