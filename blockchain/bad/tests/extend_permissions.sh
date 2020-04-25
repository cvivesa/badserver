####################################################
# Cleos command that extends permission to the superfuture contact to act on
# the users behalf, Needed to prevent the contract from holding too much collateral
####################################################

#extend permissons
cleos set account permission tester1  active '{"threshold":1,"keys":[{"key":"EOS6aDS41q9Lfjkot8PASmKoK3Ru3oJHueSpDMUkN3SGuDddvtBrS","weight":1}], "accounts":[{"permission":{"actor":"superfuture","permission":"eosio.code"},"weight":1}], "waits":[] }' owner -p tester1
