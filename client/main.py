import logging
from client.analyzer.SteamAnalyzer import SteamAnalyzer
from common.broker.Broker import Broker

def callback(ch, method, properties, body):
    logging.info(f" Se recibio el sgt: mensaje: {body}")
    # printear => metodos propiedades o ch son objetos. 

#  TODO: Main por ahora asi para hacer el Broker,
#  luego deben quedar solo las 2 lineas de abajo y el import de SteamAnalyzer

def main():
    broker = Broker()
    broker.create_queue('hello')
    broker.assign_callback(queue_name='hello', call_back =callback)
    broker.start_consuming()

    #analyzer = SteamAnalyzer()
    #analyzer.get_result_from_queries()

main()

