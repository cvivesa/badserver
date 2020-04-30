#unlock the wallet
cleos wallet open
cleos wallet unlock < wallet_key.txt


#Creates test accounts
cleos create account eosio admin EOS6aDS41q9Lfjkot8PASmKoK3Ru3oJHueSpDMUkN3SGuDddvtBrS
cleos create account eosio tester1 EOS6aDS41q9Lfjkot8PASmKoK3Ru3oJHueSpDMUkN3SGuDddvtBrS
cleos create account eosio tester2 EOS6aDS41q9Lfjkot8PASmKoK3Ru3oJHueSpDMUkN3SGuDddvtBrS
cleos create account eosio tester3 EOS6aDS41q9Lfjkot8PASmKoK3Ru3oJHueSpDMUkN3SGuDddvtBrS

#Create the tim-bucks
cleos push action eosio.token create '{"issuer":"admin", "maximum_supply":"1000000.00 TBK"}' -p eosio.token@active
#Issue them
cleos push action eosio.token issue '["admin", "1000.00 TBK", "memo"]' -p admin@active
cleos push action eosio.token transfer '["admin", "tester1", "100.00 TBK", "memo"]' -p admin@active
cleos push action eosio.token transfer '["admin", "tester2", "100.00 TBK", "memo"]' -p admin@active
cleos push action eosio.token transfer '["admin", "tester3", "100.00 TBK", "memo"]' -p admin@active

