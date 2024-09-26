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

#si esta queue del otro lado es durable aca tambien tiene que ser durable.sino falla!.
channel.queue_declare(queue='task_queue', durable=True)
print('[{}] Waiting for messages. To exit press CTRL+C'.format(consumer_id))


def callback(ch, method, properties, body):
    print("[{}] Received {}".format(consumer_id, body))
    if consumer_id == "1":
        print(f"Sleeping consumer with {consumer_id} ")
        time.sleep(5)
    # TODO: process the data y guardarlo o pasarserlo a otra etapa o proceso o algo.  TP1. 
    print("[{}] Done".format(consumer_id))
    # usamos el basic_ack para decirle a rabbitmq que ya procesamos el mensaje.
    ch.basic_ack(delivery_tag=method.delivery_tag)


# Basicamente le decimos q envia el paquete al debe menos acks.
# Consumer 2 saca rapidamente el mensaje y la queue no va a crecer.  
#channel.basic_qos(prefetch_count=1)

# le pasamos la queue a leer y la callback a procesar.
channel.basic_consume(queue='task_queue', on_message_callback=callback)

channel.start_consuming()