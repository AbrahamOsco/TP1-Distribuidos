from system.controllers.Input import Input
from common.broker.Broker import Broker
import time 

# TODO refactorizar main luego de tener la api del broker completa. 
def main():
    broker = Broker()
    broker.create_queue(queue_name ='hello')
    for i in range(100):
        broker.public_message(queue_name='hello', message='Hello world 🔥')
        print(" 🔥 [x] Sent 'Hello World {}!'".format(i))
        time.sleep(1)

    broker.close()
    #a_input = Input()
    #a_input.run()

main()


