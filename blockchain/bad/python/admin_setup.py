# Here is some python to do the admin set up
import shlex, json
import subprocess

def run_cmd(command):
    return subprocess.check_output(shlex.split(command))

cmd_list = [
    "cleos wallet open",
    "cleos wallet unlock < wallet_key.txt",
    "cleos create account eosio admin EOS6aDS41q9Lfjkot8PASmKoK3Ru3oJHueSpDMUkN3SGuDddvtBrS",
    "cleos push action eosio.token create '{\"issuer\":\"admin\", \"maximum_supply\":\"1000000.00 TBK\"}' -p eosio.token@active",
    "cleos push action eosio.token issue '[\"admin\", \"1000000.00\", \"memo\"]' -p admin@active"]

def setup_admin():
    for cmd in cmd_list:
        run_cmd(cmd)
