# TP Escalabilidad

## Instrucciones de uso

Para generar el archivo docker compose se debe correr el comando: 
* **./generar-compose.sh docker-compose-dev.yaml**

Al correr dicho comando preguntara cuantos clientes desea correr y luego por cada uno los porcentajes para las ejecuciones que desea hacer con ese cliente por ejemplo, si quisiera hacer 2 ejecuciones para un cliente con el 10% y el 30% el dataset deberia poner 0.1,0.3. Luego preguntara si desea ejecutar todas las consultas, ingresando S ejecutara las 5 consultas, caso contrario pedira que se ingrese el numero de consulta que se desea ejecutar (se debe ingresar un numero entre 1 y 5). Luego preguntara si desea seleccionar cantidad de nodos, esto permite escalar los mismos, ingresando S preguntara por cada nodo que se puede escalar cuantos se desea utilizar, caso contrario utilizara por defecto 1 nodo de cada tipo

Finalmente se puede correr utilizando 

* **./run.sh**
