docker build -f ./system/controllers/input/Dockerfile -t "input:latest" .
docker build -f ./system/controllers/select/selectQ1/Dockerfile -t "selectq1:latest" .
docker build -f ./client/Dockerfile -t "client:latest" .

#docker build -f ./system/filters/selectIDName/Dockerfile -t "selectidname:latest" .
#docker build -f ./system/filters/filterDecade/Dockerfile -t "filterdecade:latest" .
#docker build -f ./system/filters/filterGender/Dockerfile -t "filtergender:latest" .
#docker build -f ./system/filters/filterReviewEnglish/Dockerfile -t "filterreviewenglish:latest" .
#docker build -f ./system/filters/filterScoreXPositives/Dockerfile -t "filterscorexpositives:latest" .
#docker build -f ./system/filters/filterScorePositive/Dockerfile -t "filterscorepositive:latest" .
#docker build -f ./system/groupers/grouperTopReviewsPositiveIndie/Dockerfile -t "groupertopreviewspositiveindie:latest" .
#docker build -f ./system/groupers/grouperTopAveragePlaytime/Dockerfile -t "groupertopaverageplaytime:latest" .
#docker build -f ./system/groupers/platformCounter/Dockerfile -t "platformcounter:latest" .
docker compose -f docker-compose-dev.yaml up -d
docker compose -f docker-compose-dev.yaml logs -f
#docker compose -f docker-compose-dev.yaml down -t 7
#docker compose -f docker-compose-dev.yaml up
