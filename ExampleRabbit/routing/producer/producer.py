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

#El nombre del exchange debe ser un variable de entorno strins y no harcodeado.  tipo direct 
# creamos un exchange de nombre direct_logs y tipo direct
channel.exchange_declare(exchange='direct_logs', exchange_type='direct')
severity = ["error", "info", "debug"]

for i in range(100):
    log_level = severity[random.randint(0,2)]
    message = "[{}] Log with random severity".format(log_level)

    # EN el helloworld el routin_key significaba el nombre de la queue. 
    #Le pasamos el nombre del exchange y routing key signfica key usada en el exchange.   
    channel.basic_publish(exchange='direct_logs', routing_key=log_level, body=message)
    print(" [x] Sent %r" % message)
    time.sleep(1)

connection.close()
