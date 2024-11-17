docker kill $(docker ps -aq)
docker rm $(docker ps -aq)
docker build -f ./system/leader/Dockerfile -t "leader:latest" .
docker build -f ./system/leader/nodeToy/Dockerfile -t "nodetoy:latest" .


docker compose -f dockerLeaderCompose.yaml up -d --build
docker compose -f dockerLeaderCompose.yaml logs -f

# Kill a particular container: 
# docker stop -t 7 my_container

# Kill all
# docker compose -f dockerLeaderCompose.yaml stop -t 7
# docker compose -f docker-compose-dev.yaml down