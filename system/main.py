from system.controllers.Input import Input
from common.broker.Broker import Broker
import logging
import random as r 
import time 

# TODO refactorizar main luego de tener la api del broker completa. 
def main():
    broker = Broker()

    # Se crea una  queue de 'name task_queue' y es durable (solo la queue). 
    # Un message es durable <=>  si la queue y el message son durables.
    broker.create_queue(name ='task_queue', durable =True) #Si la queue ya es durable el Broker ya hace todos sus mensajes durable esta encapsulado.
    
    # Creamos 3 exchanges le decimos su name y el tipo 
    broker.create_exchange(name='logs', exchange_type= 'fanout')
    broker.create_exchange(name='direct_logs', exchange_type='direct')
    broker.create_exchange(name='topic_querys', exchange_type='topic')

    games_shooter = ['CSGO', 'Valorant', 'Fortnite', 'PUBG', 'Apex', 'Overwatch', 'Rainbow6']
    review_games = ['Ruined my life', 'I love it', 'I hate it', 'I dont know', 'I dont care']
    message = ["🔥", "⌚ ", "🧮", "🧑‍🚀"]
    severities = ["High", "Medium", "Low"]
    for i in range(50):
        severity = r.choice(severities)
        game_shoter = r.choice(games_shooter)
        review_game = r.choice(review_games)
        #publicamos un mensaje a la QUEUE, no a un exchange! (ejemplo de juguete)
        broker.public_message(queue_name='task_queue', message=f'Message to queue task_Queue 🤯 {r.choice(message)}-{r.choice(message)}')
        
        # Si no hay queues asociadas a este exchange cuando se pushean mensajes se perderan los mensajes, ver como hacerlo durable
        broker.public_message(exchange_name='logs', message=f'Message to Exchange logs 🎖️ 💯 {r.choice(message)}')
        broker.public_message(exchange_name ='direct_logs', routing_key =severity, message=f'Message to exchange direct_logs 🚡 {severity}')
        broker.public_message(exchange_name ='topic_querys', routing_key =f'games.q1', message =f'Send a game {game_shoter} 🏺')
        broker.public_message(exchange_name ='topic_querys', routing_key =f'reviews.otherWorld', message =f'Send a review {review_game} 🗡️')
        time.sleep(0.1)

    broker.close()
    
    #a_input = Input()
    #a_input.run()

main()


