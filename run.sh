docker build -f ./system/Dockerfile -t "system:latest" .
docker build -f ./client/Dockerfile -t "client:latest" .
docker compose -f docker-compose-dev.yaml up -d
docker compose -f docker-compose-dev.yaml logs -f
docker compose -f docker-compose-dev.yaml down -t 7
