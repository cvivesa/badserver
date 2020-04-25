###################################################################
#Testing for baisc future functionality
###################################################################

# Admin makes some spots to have futures on
cleos push action superfuture createsublot '["4","3","admin","2600000000","2610000001"]' -p admin@active

#Now the school offers them for sale
cleos push action superfuture crtfuture '["","admin","4","0","2600000001","2610000000","2600000000","1 TBK","15"]' -p admin@active

#And somebody buys them
cleos push action superfuture cptfuture '["tester1","","2","2","2600000001","2610000000","2600000000","1.00 TBK","15"]' -p tester1@active
