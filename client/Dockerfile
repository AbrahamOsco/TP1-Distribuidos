FROM python:3.9.20-alpine3.19
RUN apk update && apk add --no-cache python3-dev py3-pip
COPY client /app/client
COPY common /app/common
ENTRYPOINT ["/bin/sh"]
