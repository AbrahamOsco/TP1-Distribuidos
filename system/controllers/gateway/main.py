from system.controllers.gateway.Gateway import Gateway
import signal

def main():
    gateway = Gateway()
    signal.signal(signal.SIGTERM, lambda _n,_f: gateway.abort())
    gateway.run()

main()
