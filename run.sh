docker build -f ./system/Dockerfile -t "system:latest" .
docker build -f ./client/Dockerfile -t "client:latest" .
docker build -f ./FilterDecade2010/Dockerfile -t "FilterDecade2010:latest" .
docker build -f ./FilterGender/Dockerfile -t "FilterGender:latest" .
docker build -f ./FilterReviewEnglish/Dockerfile -t "FilterReviewEnglish:latest" .
docker build -f ./FilterScore5kPositives/Dockerfile -t "FilterScore5kPositives:latest" .
docker build -f ./GrouperTop5ReviewsPositives/Dockerfile -t "GrouperTop5ReviewsPositives:latest" .
docker build -f ./GrouperTop10AveragePlaytime/Dockerfile -t "GrouperTop10AveragePlaytime:latest" .
docker build -f ./PlatformCounter/Dockerfile -t "PlatformCounter:latest" .
docker build -f ./PlatformReducer/Dockerfile -t "PlatformReducer:latest" .
docker compose -f docker-compose-dev.yaml up -d
docker compose -f docker-compose-dev.yaml logs -f
docker compose -f docker-compose-dev.yaml down -t 7
