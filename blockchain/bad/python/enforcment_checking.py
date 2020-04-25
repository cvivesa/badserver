#######################################################
# Check the blockchain to see who can park in a sublot
#######################################################

import shlex, json
import subprocess

def run_cmd(command):
    return subprocess.check_output(shlex.split(command))

def get_table(table):
    return run_cmd("cleos get table superfuture superfuture -l 1000 "+table)

#user as string
def get_user_groups(user):
    info = json.loads(get_table("mstructs"))
    groups = []
    for i in range(0, len(info['rows'])):
        mstruct = info['rows'][i]
        if(mstruct['member'] == user):
            groups.append(mstruct['group_id'])
    return groups

def get_group_members(group_id):
    info = json.loads(get_table("mstructs"))
    member_arr = []
    for i in range(0, len(info['rows'])):
        mstruct = info['rows'][i]
        if(mstruct['group_id'] == group_id):
            member_arr.append(mstruct['member'])
    return member_arr

def get_allowed_users(sublot_id, time):
    #get all the stranfers
    info = json.loads(get_table("stransfers"))
    spot_arr =[[0 for col in range(3)] for row in range(100)]
    for i in range(0, len(info['rows'])):
        if(info['rows'][i]['sublot_id'] == str(sublot_id)):
            stranfer = info['rows'][i]
            if(stranfer[transfer_time] < time and stranfer[transfer_time]>spot_arr[int(stransfer['spot_id'])][2]):
                spot_arr[int(stransfer['spot_id'])] = [stranfer[to],stranfer[to_group_id],stranfer[transfer_time]]
    owner_arr = []
    group_arr = []
    for spot in spot_arr:
        owner_arr.append(spot[0])
        group_arr.append(spot[1])
    for group_id in group_arr:
        owner_arr.extend(get_group_members(group_id))
    return list(set(owner_arr))

def get_allowed_spots(name, time, num_sublots):
    groups = get_user_groups(name)
    lot_arr = [[[0 for col in range(4)] for transfer in range(100)] for spot in range(1,num_sublots+1)]
    for i in range(0, len(info['rows'])):
        stranfer = info['rows'][i]
        if(stranfer[transfer_time] < time and stranfer[transfer_time]>lot_arr[int(stranfer['sublot_id'])][int(stransfer['spot_id'])][2]):
            lot_arr[int(stranfer['sublot_id'])][int(stransfer['spot_id'])] = [stranfer[to],stranfer[to_group_id],stranfer[transfer_time],int(stransfer['spot_id'])]
    allowed_spots = []
    for lot in lot_arr:
        for spot in lot:
            if(spot[0] == user or spot[1] in groups):
                allowed_spots.append(spot[3])
