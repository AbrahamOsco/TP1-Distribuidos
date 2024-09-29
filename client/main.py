import logging
import random as r
import time as t
from client.analyzer.SteamAnalyzer import SteamAnalyzer
from common.broker.Broker import Broker


def callback_generica(ch, method, properties, body):
    logging.info(f"Se Recibe : 👉{body.decode()} with routing key: {method.routing_key}")
    t.sleep(2)
    #logging.info(f" Message ready! 🔨 🛠️ 🇱")
    ch.basic_ack(delivery_tag=method.delivery_tag) # Enviamos un ack a mano y 'adecuado' luego de acabar la tarea
    # Incluso si hay un consumidor muere 🪦 los mensajes no se pierden, se debe enviar el ack al mismo channel q recibio. 

def main():
    broker = Broker()
    # Queue q hago en el producer, queue que hago en el consumer, con el mismo name y el tipo de durable
    # El callback va por lo general del lado de los consumers.
    broker.create_queue(name ='task_queue', durable =True, callback =callback_generica)
    queue_name_exchange_1 = broker.create_queue(callback =callback_generica) #Queue anonima fijate que no tiene name.
    queue_name_exchange_2 = broker.create_queue(callback =callback_generica) #Queue anonima.
    queue_direct_1 = broker.create_queue(callback =callback_generica) 
    queue_direct_2 = broker.create_queue(callback =callback_generica) 
    
    name_games_q1 = broker.create_queue(callback =callback_generica)
    name_games_q2345 = broker.create_queue(callback =callback_generica)
    name_review = broker.create_queue(callback =callback_generica)
    
    #Creamos los exchange con su tipo y nombre
    broker.create_exchange(name='logs', exchange_type= 'fanout')
    broker.create_exchange(name='direct_logs', exchange_type='direct')
    broker.create_exchange(name='topic_querys', exchange_type='topic')
    #En los topics colocamos aca las binding keys con patrones ej: 'games.*' 'review.*', etc
    
    #Bindeamos el exchange a la queue y si es de tipo direct/topic le pasamos la binding key (la key de la queue).
    broker.bind_queue(exchange_name ='logs', queue_name =queue_name_exchange_1)
    broker.bind_queue(exchange_name ='logs', queue_name =queue_name_exchange_2)
    broker.bind_queue(exchange_name ='direct_logs', queue_name =queue_direct_1, binding_key ='High')
    broker.bind_queue(exchange_name ='direct_logs', queue_name =queue_direct_2, binding_key ='Medium')
    broker.bind_queue(exchange_name='topic_querys', queue_name =name_games_q1, binding_key='games.*')
    broker.bind_queue(exchange_name='topic_querys', queue_name =name_games_q2345, binding_key='games.*')
    broker.bind_queue(exchange_name='topic_querys', queue_name =name_review, binding_key='reviews.*')


    # Habilitamos q cuando mandemos una task el worker libre la toma 
    # Esto en el caso de queues peladas (mira la task_queue de arriba) es una worker_queue
    broker.enable_worker_queues()

    # Nos bloqueamos y emepzamos a consumir hay q handlear alguna singla pa terminar prolijamente.
    broker.start_consuming()
    broker.close()

    #analyzer = SteamAnalyzer()
    #analyzer.get_result_from_queries()

main()

