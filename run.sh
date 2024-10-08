chmod +x run.sh stop.sh
./stop.sh
docker build -f ./client/Dockerfile -t "client:latest" .
docker build -f ./system/rabbitmq/Dockerfile -t "rabbit:latest" .
docker build -f ./system/controllers/gateway/Dockerfile -t "gateway:latest" .
docker build -f ./system/controllers/filters/filterBasic/Dockerfile -t "filterbasic:latest" .
docker build -f ./system/controllers/select/selectQ1/Dockerfile -t "selectq1:latest" .
docker build -f ./system/controllers/groupers/platformCounter/Dockerfile -t "platformcounter:latest" .
docker build -f ./system/controllers/reducers/platformReducer/Dockerfile -t "platformreducer:latest" .
docker build -f ./system/controllers/select/selectQ2345/Dockerfile -t "selectq2345:latest" .
docker build -f ./system/controllers/filters/filterGender/Dockerfile -t "filtergender:latest" .
docker build -f ./system/controllers/filters/filterDecade/Dockerfile -t "filterdecade:latest" .
docker build -f ./system/controllers/groupers/grouperTopAvgPlaytime/Dockerfile -t "groupertopavgplaytime:latest" .
docker build -f ./system/controllers/filters/filterScorePositive/Dockerfile -t "filterscorepositive:latest" .


#docker build -f ./system/controllers/select/selectIDName/Dockerfile -t "selectidname:latest" .
#docker build -f ./system/controllers/filters/filterReviewEnglish/Dockerfile -t "filterreviewenglish:latest" .
#docker build -f ./system/controllers/filters/filterScoreXPositives/Dockerfile -t "filterscorexpositives:latest" .
#docker build -f ./system/controllers/filters/filterScorePositive/Dockerfile -t "filterscorepositive:latest" .
#docker build -f ./system/controllers/groupers/grouperTopReviewsPositiveIndie/Dockerfile -t "groupertopreviewspositiveindie:latest" .
#docker build -f ./system/controllers/groupers/grouperTopAveragePlaytime/Dockerfile -t "groupertopaverageplaytime:latest" .
docker compose -f docker-compose-dev.yaml up -d
docker compose -f docker-compose-dev.yaml logs -f
#docker compose -f docker-compose-dev.yaml down -t 7
#docker compose -f docker-compose-dev.yaml up
