docker stop -t 7 medic_2
docker stop -t 7 medic_1
docker stop -t 7 medic_0
docker stop -t 7 medic_3
docker compose -f dockerLeaderCompose.yaml stop -t 15