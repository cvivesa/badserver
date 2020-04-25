# Here is some python to do the contract set up
import shlex, json
import subprocess

def run_cmd(command):
    return subprocess.check_output(shlex.split(command))

cmd_list = [
    "cleos wallet open",
    "cleos wallet unlock < wallet_key.txt",
    "cleos create account eosio eosio.token EOS6aDS41q9Lfjkot8PASmKoK3Ru3oJHueSpDMUkN3SGuDddvtBrS",
    "cleos set contract eosio.token ../../eosio.token --abi eosio.token.abi -p eosio.token@active",
    "cleos create account eosio superfuture EOS6aDS41q9Lfjkot8PASmKoK3Ru3oJHueSpDMUkN3SGuDddvtBrS",
    "cleos set contract superfuture ../superfuture -p superfuture@active",
    "cleos set account permission superfuture active --add-code"]


def setup_contracts():
    for cmd in cmd_list:
        run_cmd(cmd)
