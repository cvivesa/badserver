#test the creation of options in the error free route

#set -x

NOW=$(date '+%s')

SUBLOT=`expr $NOW % 1000`

WHOLE_ID=`expr $SUBLOT + 1000`

PRICE1="1.00 TBK"
PRICE2="2.00 TBK"
PRICE3="0.50 TBK"

#First to make some spots
cleos push action superfuture createsublot [\"$SUBLOT\",\"1\",\"admin\",\"`expr $NOW + 5`\",\"2610000001\"] -p admin@active

##################################################### Should be exercised
#make a half admin is seller and putter on an option with a owned future
DATA="[\"\",\"admin\",\"\",\"admin\",\"$SUBLOT\",\"`expr $NOW + 10`\",\"`expr $NOW + 30`\",\"`expr $NOW + 9`\",\"`expr $NOW + 5`\",\""$PRICE1"\",\""$PRICE2"\",\""$PRICE3"\"]"
cleos push action superfuture crtoption "$DATA" -p admin@active
#complete the half with whole_id = WHOLE_ID
DATA="[\"tester1\",\"\",\"tester1\",\"\",\"$SUBLOT\",\"`expr $NOW + 10`\",\"`expr $NOW + 30`\",\"`expr $NOW + 9`\",\"`expr $NOW + 5`\",\""$PRICE1"\",\""$PRICE2"\",\""$PRICE3"\",\"$WHOLE_ID\"]"
cleos push action superfuture cptoption "$DATA" -p tester1@active

#################################################### Should transfer collateral to caller
# Making an option in which admin does not own a spot
#cleos push action superfuture crtoption '["","admin","","admin","101","`expr NOW + 10`","`expr NOW + 30`","`expr NOW + 9`","`expr NOW + 5`","1 TBK","2 TBK","0.5 TBK"]' -p admin@active
DATA="[\"\",\"admin\",\"\",\"admin\",\"1001\",\"`expr $NOW + 10`\",\"`expr $NOW + 30`\",\"`expr $NOW + 9`\",\"`expr $NOW + 5`\",\""$PRICE1"\",\""$PRICE2"\",\""$PRICE3"\"]"
cleos push action superfuture crtoption "$DATA" -p admin@active

#cleos push action superfuture cptoption '["tester1","","tester1","","101","`expr NOW + 10`","`expr NOW + 30`","`expr NOW + 9`","`expr NOW + 5`","1.00 TBK","2.00 TBK","0.50 TBK","`expr $WHOLE_ID + 1`"]' -p tester1@active
DATA="[\"tester1\",\"\",\"tester1\",\"\",\"1001\",\"`expr $NOW + 10`\",\"`expr $NOW + 30`\",\"`expr $NOW + 9`\",\"`expr $NOW + 5`\",\""$PRICE1"\",\""$PRICE2"\",\""$PRICE3"\",\"`expr $WHOLE_ID + 1`\"]"
cleos push action superfuture cptoption "$DATA" -p tester1@active

###############################################
#Wait for options to be valid
sleep 1

################################################# Testing the first option
echo "should fail contract has not expired"
DATA="[\"admin\",\"$WHOLE_ID\"]"
echo cleos push action superfuture clmcollat "$DATA" -p admin@active

echo "Should fail putter is not the buyer"
DATA="[\"tester1\",\"admin\",\"$WHOLE_ID\"]"
cleos push action superfuture exrput "$DATA" -p admin@active

echo "Should work and create the future"
#cleos push action superfuture exrcall '["tester1","admin","$WHOLE_ID"]' -p tester1@active
DATA="[\"tester1\",\"admin\",\"$WHOLE_ID\"]"
cleos push action superfuture exrcall "$DATA" -p tester1@active

################################################ Testing the second option
echo "Should pass but not create future and transfer collateral"
#cleos push action superfuture exrcall '["tester1","admin","`expr $WHOLE_ID + 1`"]' -p tester1@active
DATA="[\"tester1\",\"admin\",\"`expr $WHOLE_ID + 1`\"]"
cleos push action superfuture exrcall "$DATA" -p tester1@active
