#!/usr/bin/env python3
import pika
import time

#Creamos una conexion: 
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbitmq')) #el host aca es la ip del rabbitmq (vemos en el service de docker-compose rabbitmq)

#Creamos un channel al broker: 
channel = connection.channel()

#Creamos una queue de nombre "hello"
channel.queue_declare(queue='hello')

for i in range(100):
    # Usamos el chanel con el metodo basic_publish para enviar el mensaje "Hello world{i}!"
    #  a la queue "hello" (en este ej basico)
    channel.basic_publish(exchange='', routing_key='hello', body='Hello World {}!'.format(i))
    print(" 🔥 [x] Sent 'Hello World {}!'".format(i))
    time.sleep(1)

connection.close()
