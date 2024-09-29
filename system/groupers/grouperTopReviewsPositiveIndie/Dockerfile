FROM python:3.9.20-alpine3.19
RUN apk update && apk add --no-cache python3-dev py3-pip
RUN pip install pika
COPY system/groupers/grouperTopReviewsPositiveIndie /app/system/groupers/grouperTopReviewsPositiveIndie
COPY system/utils /app/system/utils
COPY common /app/common
ENTRYPOINT ["/bin/sh"]

