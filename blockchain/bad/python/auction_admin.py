#######################################################
# Check the blockchain to see who can park in a sublot
#######################################################

import shlex, json, re
import subprocess

def run_cmd(command):
    return subprocess.check_output(shlex.split(command))

def get_balance(user):
    info = (run_cmd("cleos get currency balance eosio.token "+user+" TBK"))
    return re.findall("\d+\.\d+",info)

def get_table(table):
    return run_cmd("cleos get table superfuture superfuture -l 1000 "+table)

def get_halves(num_sublots, max_num_spots):
    info = json.loads(get_table("halves"))
    sublot_arr =[[[] for col in range(max_num_spots)] for row in range(num_sublots)]
    for i in range(0, len(info['rows'])):
        half = info['rows'][i]
        if(half[start_time] == start_time and half[end_time] == end_time):
            sublot_arr[half['sublot_id']][half['spot_id']].append(half)
    for sublot in sublot_arr:
        for spot in sublot:
            sorted_halves = sorted(spot, key=lambda s: s['price'])
            for h in sorted_halves:
                if(get_balance(h['buyer']) > h['price']):
                    complete_future("admin",h['buyer'],"admin", h['sublot_id'], h['spot_id'], h['start_time'], h['end_time'], h['request_expiration_time'], h['price'], h['future_id'])
                    break
