#Setup user and contracts for eosio.token and superfutures

#eosio.token
cleos create account eosio eosio.token EOS6aDS41q9Lfjkot8PASmKoK3Ru3oJHueSpDMUkN3SGuDddvtBrS
cleos set contract eosio.token ../../eosio.token --abi eosio.token.abi -p eosio.token@active

#superfutures
cleos create account eosio superfuture EOS6aDS41q9Lfjkot8PASmKoK3Ru3oJHueSpDMUkN3SGuDddvtBrS
cleos set contract superfuture ../superfuture -p superfuture@active
cleos set account permission superfuture active --add-code
