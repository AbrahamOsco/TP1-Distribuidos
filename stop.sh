docker rm -f client1 rabbitmq gateway platformreducer
docker rm -f filterbasic_1 filterbasic_2 filterbasic_3  
docker rm -f selectQ1_1 selectQ1_2  selectQ1_3
docker rm -f platformcounter_1 platformcounter_2 
docker rm -f selectq2345_1 selectq2345_2 selectq2345_3
docker rm -f filtergender_1 filtergender_2 filtergender_3 
docker rm -f filterdecade_1 filterdecade_2
docker rm -f groupertopavgplaytime    


docker network rm -f tp2_system_network
