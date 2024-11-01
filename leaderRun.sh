docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker build -f ./system/leader/Dockerfile -t "leader:latest" .


docker compose -f dockerLeaderCompose.yaml up -d --build
docker compose -f dockerLeaderCompose.yaml logs -f

