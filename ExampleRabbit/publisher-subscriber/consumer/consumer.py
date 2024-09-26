#!/usr/bin/env python3
import pika
import time
import os

# Wait for rabbitmq to come up
time.sleep(10)

consumer_id = os.environ["CONSUMER_ID"]
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()

#Hacemos el '.exchange_declare' idem q el producer.
channel.exchange_declare(exchange='logs', exchange_type='fanout')

# Creamos una queue anonima => con un name vacio => (le decimos a rabbit q defina el nombre de la queue) 
result = channel.queue_declare(queue='', durable=True)

# Le pedimos el nombre q rabbit le puso a la queue.
queue_name = result.method.queue

# Hacemos el bind con el exchange! :
channel.queue_bind(exchange='logs', queue=queue_name)

print('[{}] Waiting for messages. To exit press CTRL+C'.format(consumer_id))

def callback(ch, method, properties, body):
    print("[{}] Received {}".format(consumer_id, body))

channel.basic_qos(prefetch_count=1)

# ponemos la queue de la cual vamos a recibir mensajes y NO ❌ el exchange.
channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()