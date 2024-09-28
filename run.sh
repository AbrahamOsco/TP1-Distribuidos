docker build -f ./common/broker/Dockerfile -t "rabbit:latest" .
docker build -f ./system/Dockerfile -t "system:latest" .
docker build -f ./client/Dockerfile -t "client:latest" .
docker build -f ./filterDecade2010/Dockerfile -t "filterdecade2010:latest" .
docker build -f ./filterGender/Dockerfile -t "filtergender:latest" .
docker build -f ./filterReviewEnglish/Dockerfile -t "filterreviewenglish:latest" .
docker build -f ./filterScore5kPositives/Dockerfile -t "filterscore5kpositives:latest" .
docker build -f ./grouperTop5ReviewsPositives/Dockerfile -t "groupertop5reviewspositives:latest" .
docker build -f ./grouperTop10AveragePlaytime/Dockerfile -t "groupertop10averageplaytime:latest" .
docker build -f ./platformCounter/Dockerfile -t "platformcounter:latest" .
docker build -f ./platformReducer/Dockerfile -t "platformreducer:latest" .
docker compose -f docker-compose-dev.yaml up -d
docker compose -f docker-compose-dev.yaml logs -f
docker compose -f docker-compose-dev.yaml down -t 7
