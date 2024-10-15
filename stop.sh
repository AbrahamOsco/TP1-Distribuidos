docker rm -f client1 rabbitmq gateway 
docker rm -f filterbasic_1 filterbasic_2 filterbasic_3  
docker rm -f selectq1_1 selectq1_2  selectq1_3
docker rm -f platformcounter_1 platformcounter_2 platformreducer_1 
docker rm -f selectq2345_1 selectq2345_2 selectq2345_3
docker rm -f filtergender_1 filtergender_2 filtergender_3 
docker rm -f filterdecade_1 filterdecade_2 groupertopavgplaytime_1
docker rm -f filterscorepositive_1 filterscorepositive_2 filterscorepositive_3
docker rm -f selectidname_1 selectidname_2 selectidname_3    
docker rm -f monitorstorageq3_1 groupertoppositivereviews_1
docker rm -f filterscorenegative_1 filterscorenegative_2
docker rm -f monitorstorageq4_1  filterreviewsenglish_1
docker rm -f monitorstorageq5_1  grouperpercentile_1


docker network rm -f tp2_system_network
