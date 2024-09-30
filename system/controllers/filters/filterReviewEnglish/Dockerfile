FROM python:3.9.20-alpine3.19
RUN apk update && apk add --no-cache python3-dev py3-pip
RUN pip install pika
COPY system/controllers/filters/filterReviewEnglish /app/system/controllers/filters/filterReviewEnglish
COPY system/commonsSystem /app/system/commonsSystem
COPY common /app/common
ENTRYPOINT ["/bin/sh"]

