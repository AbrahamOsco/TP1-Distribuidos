# Bienvenido a la rama DOJO, el lugar pefecto para hacer katas ⚔️
###  En la carpeta ExampleRabbitMQ:
1. Ir a la carpeta base-images
1. Dar permisos con chmod +x  y ejecutar: ./build.sh
1. Ir a la carpeta por ej: hello_world:
1. Dar permisos y ejecutar: ./run.sh y to clean use: ./stop.sh.
1. Idem a otras carpetas publisher-subscriber, routing, work-queues. Leer comentarios


## Instrucciones de uso

Para generar el archivo docker compose se debe correr el comando: 
* **./generar-compose.sh docker-compose-dev.yaml**

Luego se puede construir los contenedores usando 

* **docker-compose -f docker-compose-dev.yaml build**

Finalmente se puede correr los mismos usando

* **docker-compose -f docker-compose-dev.yaml up**
