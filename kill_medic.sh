docker stop -t 15 medic_0
docker stop -t 15 medic_3
docker stop -t 15 medic_2
docker stop -t 15 medic_1
docker compose -f dockerLeaderCompose.yaml stop -t 20