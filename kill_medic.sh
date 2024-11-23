docker stop -t 150 medic_3
docker stop -t 150 medic_2
docker stop -t 150 medic_1
docker stop -t 150 medic_0
docker compose -f dockerLeaderCompose.yaml stop -t 100