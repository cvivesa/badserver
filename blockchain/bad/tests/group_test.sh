#Testing groups and their functions
cleos push action superfuture crtgroup '["agrp2","admin","1.00 TBK","1.0","1"]' -p admin@active


cleos push action superfuture joingroup '["tester1","1"]' -p tester1@active

#cleos push action superfuture ftrtogrp '["admin","2","0"]' -p admin@active

#cleos push action superfuture crtgroup '["tgrp11","tester1","1.00 TBK","1.0","24"]' -p tester1@active

#cleos push action superfuture ftrtogrp '["tester1","7","7"]' -p tester1@active

#cleos push action superfuture ftrfrmgrp '["tester1","7","7"]' -p tester1@active

#cleos push action superfuture joingroup '["tester2","24"]' -p tester2@active
