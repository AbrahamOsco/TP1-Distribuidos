from system.controllers.gateway.Gateway import Gateway

def main():
    gateway = Gateway()
    gateway.run()
    gateway.close() 

main()
