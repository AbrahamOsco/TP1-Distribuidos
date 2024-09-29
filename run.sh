docker build -f ./system/broker/Dockerfile -t "rabbit:latest" .
docker build -f ./system/Dockerfile -t "system:latest" .
docker build -f ./client/Dockerfile -t "client:latest" .
docker build -f ./filterDecade/Dockerfile -t "filterdecade:latest" .
docker build -f ./filterGender/Dockerfile -t "filtergender:latest" .
docker build -f ./filterReviewEnglish/Dockerfile -t "filterreviewenglish:latest" .
docker build -f ./filterScoreXPositives/Dockerfile -t "filterscorexpositives:latest" .
docker build -f ./grouperTopReviewsPositiveIndie/Dockerfile -t "groupertopreviewspositiveindie:latest" .
docker build -f ./grouperTopAveragePlaytime/Dockerfile -t "groupertopaverageplaytime:latest" .
docker build -f ./platformCounter/Dockerfile -t "platformcounter:latest" .
docker build -f ./platformReducer/Dockerfile -t "platformreducer:latest" .
docker compose -f docker-compose-dev.yaml up -d
docker compose -f docker-compose-dev.yaml logs -f
docker compose -f docker-compose-dev.yaml down -t 7
docker compose -f docker-compose-dev.yaml up
