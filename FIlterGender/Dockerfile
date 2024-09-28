FROM python:3.9.7-slim
WORKDIR /app
COPY FilterGender /app/FilterGender
COPY common /app/common
RUN pip install pika

ENTRYPOINT ["python3", "/app/FilterGender/main.py"]
