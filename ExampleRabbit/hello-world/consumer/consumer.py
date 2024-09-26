#!/usr/bin/env python3
import pika
import time

# Creamos  una conexion al broker
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbitmq'))

# creamos un channel al broker
channel = connection.channel()

#Si la queue no existe la crea, si existe no hace nada
channel.queue_declare(queue='hello') 

def callback(ch, method, properties, body):
    print(" 🐃[x] Received %r" % body)

# Decime que queres consumir (.basic_consume) en que queue queres consumir. 
# y que queres hacer cuando consumis ese mensaje.  
channel.basic_consume(
    queue='hello', on_message_callback=callback, auto_ack=True) 
# Esto no consume nada solo setea ccomo se consume los mensajes. 

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming() #Metodo bloqueante, es el start del client.

