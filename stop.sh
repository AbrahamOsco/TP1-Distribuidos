docker stop -t 15 medic_3
docker stop -t 15 medic_2
docker stop -t 15 medic_1
docker stop -t 15 medic_0
docker compose -f docker-compose-dev.yaml stop -t 15
