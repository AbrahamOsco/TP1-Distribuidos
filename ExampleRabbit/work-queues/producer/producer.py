#!/usr/bin/env python3
import pika
import sys
import random
import time

# Wait for rabbitmq to come up
time.sleep(10)

# Create RabbitMQ communication channel
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()

# Creamos una queue de nombre task_queue  y durable (hacemos la queue persistente).
channel.queue_declare(queue='task_queue', durable=True)

for i in range(100):
    message = f"Sent Message number {i}! 🏑" 
    channel.basic_publish(
        exchange='',
        routing_key='task_queue',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent (quiero persistir el mensaje)
        ))
    print(" [x] Sent %r" % message)
    time.sleep(1)

connection.close()